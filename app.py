import os
import uuid
import requests
import streamlit as st
from vision_api import detect_food_name
from datetime import date, datetime
from PIL import Image
from streamlit_cropper import st_cropper
from cloud_storage import upload_image_to_gcs

API_URL = "http://127.0.0.1:8000"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

st.title("Food Expiration Tracker")

# Figure out if an item is fresh, expiring soon, or expired
def get_status(exp_date):
    today = date.today()

    if exp_date < today:
        return "Expired"
    elif (exp_date - today).days <= 3:
        return "Expiring Soon"
    else:
        return "Fresh"

# Save an uploaded image to the uploads folder
def save_uploaded_image(uploaded_file):
    if uploaded_file is None:
        return None

    ext = os.path.splitext(uploaded_file.name)[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    with open(file_path, "wb") as file:
        file.write(uploaded_file.getbuffer())

    return file_path

# Save a cropped image to the uploads folder
def save_cropped_image(cropped_image):
    filename = f"{uuid.uuid4().hex}_cropped.jpg"
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    cropped_image.save(file_path)
    return file_path

# ── ADD FOOD ITEM ──────────────────────────────────────────
st.header("Add Food Item")

name = st.text_input("Food Name", value=st.session_state.get("detected_name", ""))
exp_date = st.date_input("Expiration Date", value=date.today())
category = st.selectbox("Storage Location", ["Fridge", "Freezer", "Dry Pantry"])

uploaded_image = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
camera_photo = st.camera_input("Take a picture")

if uploaded_image:
    st.session_state["selected_image_path"] = save_uploaded_image(uploaded_image)

if camera_photo:
    st.session_state["selected_image_path"] = save_uploaded_image(camera_photo)

cropped_image = None

if "selected_image_path" in st.session_state:
    st.subheader("Crop Image")

    original_image = Image.open(st.session_state["selected_image_path"])

    cropped_image = st_cropper(
        original_image,
        realtime_update=True,
        box_color="#000000",
        aspect_ratio=None
    )

    st.image(cropped_image, width=350)

    if st.button("Detect Food Name"):
        temp_path = save_cropped_image(cropped_image)
        detected_name = detect_food_name(temp_path)
        st.session_state["detected_name"] = detected_name
        st.rerun()

if st.button("Add Item"):
    if name:
        image_path = None

        if cropped_image is not None:
            local_path = save_cropped_image(cropped_image)
            image_path = upload_image_to_gcs(local_path)

        requests.post(f"{API_URL}/items", json={
            "name": name,
            "expiration_date": str(exp_date),
            "image_path": image_path,
            "category": category
        })

        if "selected_image_path" in st.session_state:
            del st.session_state["selected_image_path"]

        st.success("Item added")
        st.rerun()
    else:
        st.warning("Enter a name")

# ── lIST ITEMS ─────────────────────────────────────────────
st.header("Your Items")

response = requests.get(f"{API_URL}/items")
items = response.json()

if not items:
    st.info("No items added yet.")
else:
    #Check for expired or expiring soon items and show alerts at the top
    expiring_soon = []
    expired = []

    for item in items:
        exp_date_obj = datetime.strptime(item[2], "%Y-%m-%d").date()
        status = get_status(exp_date_obj)

        if status == "Expired":
            expired.append(item[1])
        elif status == "Expiring Soon":
            expiring_soon.append(item[1])

    if expired:
        st.error(f"⚠️ {len(expired)} item(s) expired: {', '.join(expired)}")
    if expiring_soon:
        st.warning(f"🕐 {len(expiring_soon)} expiring soon: {', '.join(expiring_soon)}")

    #Loop through each category and show items grouped under it
    categories = [
        ("Fridge",     "🧊 Fridge"),
        ("Freezer",    "🔵 Freezer"),
        ("Dry Pantry", "🗄️ Dry Pantry"),
    ]

    for category_key, category_label in categories:
        # Only show items that belong to this category
        section_items = [i for i in items if (i[4] if len(i) > 4 else "Fridge") == category_key]

        if not section_items:
            continue

        st.subheader(category_label)

        for item in section_items:
            item_id       = item[0]
            item_name     = item[1]
            exp_date_text = item[2]
            image_path    = item[3]
            item_category = item[4] if len(item) > 4 else "Fridge"

            exp_date_obj   = datetime.strptime(exp_date_text, "%Y-%m-%d").date()
            status         = get_status(exp_date_obj)
            formatted_date = exp_date_obj.strftime("%B %d, %Y")

            st.write(f"**{item_name}** — {formatted_date}")

            if status == "Expired":
                st.markdown(f"**Status:** 🔴 {status}")
            elif status == "Expiring Soon":
                st.markdown(f"**Status:** 🟡 {status}")
            else:
                st.markdown(f"**Status:** 🟢 {status}")

            if image_path:
                st.image(image_path, width=350)

            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Delete {item_name}", key=f"delete_{item_id}"):
                    requests.delete(f"{API_URL}/items/{item_id}")
                    st.rerun()

            with col2:
                if st.button(f"Edit {item_name}", key=f"edit_btn_{item_id}"):
                    st.session_state[f"editing_{item_id}"] = True

            if st.session_state.get(f"editing_{item_id}"):
                new_name     = st.text_input("New Name", value=item_name, key=f"name_{item_id}")
                new_date     = st.date_input("New Expiration Date", value=exp_date_obj, key=f"date_{item_id}")
                new_category = st.selectbox(
                    "Storage Location",
                    ["Fridge", "Freezer", "Dry Pantry"],
                    index=["Fridge", "Freezer", "Dry Pantry"].index(item_category),
                    key=f"cat_{item_id}"
                )

                if st.button("Save", key=f"save_{item_id}"):
                    requests.put(f"{API_URL}/items/{item_id}", json={
                        "name": new_name,
                        "expiration_date": str(new_date),
                        "category": new_category
                    })
                    st.session_state[f"editing_{item_id}"] = False
                    st.rerun()

            st.divider()