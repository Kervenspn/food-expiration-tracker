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


# ── HELPER FUNCTIONS ───────────────────────────────────────

def get_status(exp_date):
    today = date.today()
    if exp_date < today:
        return "Expired"
    elif (exp_date - today).days <= 3:
        return "Expiring Soon"
    else:
        return "Fresh"


def days_remaining_text(exp_date):
    today = date.today()
    diff = (exp_date - today).days
    if diff < 0:
        return f"Expired {abs(diff)} day(s) ago"
    elif diff == 0:
        return "Expires today"
    elif diff == 1:
        return "Expires tomorrow"
    else:
        return f"Expires in {diff} days"


def save_uploaded_image(uploaded_file):
    if uploaded_file is None:
        return None
    ext = os.path.splitext(uploaded_file.name)[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    with open(file_path, "wb") as file:
        file.write(uploaded_file.getbuffer())
    return file_path


def save_cropped_image(cropped_image):
    filename = f"{uuid.uuid4().hex}_cropped.jpg"
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    cropped_image.save(file_path)
    return file_path


# ── RIPENESS GUIDE ─────────────────────────────────────────
produce_ripeness = {
    "Banana": {"Unripe": 5, "Ripe": 2, "Overripe": 1},
    "Avocado": {"Unripe": 7, "Ripe": 3, "Overripe": 1},
    "Apple": {"Fresh": 7},
    "Strawberry": {"Fresh": 2},
    "Mango": {"Unripe": 5, "Ripe": 2, "Overripe": 1},
    "Tomato": {"Unripe": 5, "Ripe": 3, "Overripe": 1},
    "Blueberry": {"Fresh": 3},
    "Broccoli": {"Fresh": 5},
    "Carrot": {"Fresh": 14},
    "Lettuce": {"Fresh": 5},
}

# ── ADD FOOD ITEM ──────────────────────────────────────────
st.header("Add Food Item")

food_type = st.radio("What are you adding?", ["Regular Food", "Fresh Produce"])

if food_type == "Regular Food":
    name = st.text_input("Food Name", value=st.session_state.get("detected_name", ""))
    exp_date = st.date_input("Expiration Date", value=date.today())
    is_frozen = st.checkbox("Is this going to the freezer?")
    quantity = st.number_input("Quantity", value=1, min_value=1, step=1)
    notes = st.text_area("Notes (optional)", placeholder="e.g. opened Monday, use for pasta")

    input_method = st.selectbox("How do you want to add an image?", ["Upload Image", "Take a Picture"])

    if input_method == "Upload Image":
        uploaded_image = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
        camera_photo = None
    else:
        camera_photo = st.camera_input("Take a picture")
        uploaded_image = None

    cropped_image = None

    if uploaded_image:
        st.session_state["selected_image_path"] = save_uploaded_image(uploaded_image)

    if camera_photo:
        st.session_state["selected_image_path"] = save_uploaded_image(camera_photo)

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
                "is_frozen": is_frozen,
                "notes": notes,
                "quantity": int(quantity)
            })

            if "selected_image_path" in st.session_state:
                del st.session_state["selected_image_path"]

            st.success("Item added")
            st.rerun()
        else:
            st.warning("Enter a name")

else:  # Fresh Produce
    prod_name = st.text_input("Produce Name", value=st.session_state.get("detected_produce_name", ""))

    # Ripeness selector
    common_produce = list(produce_ripeness.keys())
    selected_produce = st.selectbox("Select from common produce or choose Other", common_produce + ["Other"])

    if selected_produce == "Other":
        ripeness_input = st.text_input("Enter ripeness estimate (e.g., 'Ripe - 3 days')")
        ripeness = ripeness_input
    else:
        ripeness_options = list(produce_ripeness[selected_produce].keys())
        ripeness = st.selectbox("Ripeness", ripeness_options)

    storage = st.selectbox("Storage Location", ["Fridge", "Counter"])
    prod_quantity = st.number_input("Quantity", value=1, min_value=1, step=1)
    prod_notes = st.text_area("Notes (optional)", placeholder="e.g. spotted, soft spots")

    # Image upload for produce
    prod_input_method = st.selectbox("How do you want to add an image?", ["Upload Image", "Take a Picture"])

    if prod_input_method == "Upload Image":
        prod_uploaded_image = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"], key="prod_upload")
        prod_camera_photo = None
    else:
        prod_camera_photo = st.camera_input("Take a picture", key="prod_camera")
        prod_uploaded_image = None

    prod_cropped_image = None

    if prod_uploaded_image:
        st.session_state["prod_selected_image_path"] = save_uploaded_image(prod_uploaded_image)

    if prod_camera_photo:
        st.session_state["prod_selected_image_path"] = save_uploaded_image(prod_camera_photo)

    if "prod_selected_image_path" in st.session_state:
        st.subheader("Crop Image")
        prod_original_image = Image.open(st.session_state["prod_selected_image_path"])
        prod_cropped_image = st_cropper(
            prod_original_image,
            realtime_update=True,
            box_color="#000000",
            aspect_ratio=None
        )
        st.image(prod_cropped_image, width=350)

        if st.button("Detect Produce Name"):
            temp_path = save_cropped_image(prod_cropped_image)
            detected_name = detect_food_name(temp_path)
            st.session_state["detected_produce_name"] = detected_name
            st.rerun()

    if st.button("Add Produce"):
        if prod_name:
            image_path = None
            if prod_cropped_image is not None:
                st.write(f"DEBUG: Cropped image exists")  # Debug
                local_path = save_cropped_image(prod_cropped_image)
                st.write(f"DEBUG: Local path = {local_path}")  # Debug
                image_path = upload_image_to_gcs(local_path)
                st.write(f"DEBUG: GCS path = {image_path}")  # Debug
            else:
                st.write(f"DEBUG: Cropped image is None")  # Debug

            requests.post(f"{API_URL}/produce", json={
                "name": prod_name,
                "ripeness": ripeness,
                "storage_location": storage,
                "notes": prod_notes,
                "quantity": int(prod_quantity),
                "image_path": image_path
            })

            if "prod_selected_image_path" in st.session_state:
                del st.session_state["prod_selected_image_path"]

            st.success("Produce added")
            st.rerun()
        else:
            st.warning("Enter a produce name")

# ── YOUR ITEMS ─────────────────────────────────────────────
st.header("Your Items")

response = requests.get(f"{API_URL}/items")
items = response.json()

produce_response = requests.get(f"{API_URL}/produce")
produce_items = produce_response.json() if produce_response.status_code == 200 else []

if not items and not produce_items:
    st.info("No items added yet.")
else:
    if items:
        # Always show last added item outside expanders
        last_item = items[-1]
        remaining_items = items[:-1]

        st.subheader("🆕 Last Added Item")

        item_id = last_item[0]
        item_name = last_item[1]
        exp_date_text = last_item[2]
        image_path = last_item[3]
        is_frozen_val = last_item[4]
        item_notes = last_item[5] if len(last_item) > 5 else ""
        item_quantity = last_item[6] if len(last_item) > 6 else 1

        exp_date_obj = datetime.strptime(exp_date_text, "%Y-%m-%d").date()
        status = get_status(exp_date_obj)
        formatted_date = exp_date_obj.strftime("%b %d, %Y")
        countdown_text = days_remaining_text(exp_date_obj)

        st.write(f"**{item_name}** ({item_quantity}) — {formatted_date} ({countdown_text})")
        if status == "Expired":
            st.markdown(f"**Status:** 🔴 {status}")
        elif status == "Expiring Soon":
            st.markdown(f"**Status:** 🟡 {status}")
        else:
            st.markdown(f"**Status:** 🟢 {status}")
        if item_notes:
            st.markdown(f"**Notes:** {item_notes}")
        if image_path:
            st.image(image_path, width=350)
        col_delete, col_edit = st.columns(2)
        with col_delete:
            if st.button(f"Delete {item_name}", key=f"delete_{item_id}"):
                st.session_state[f"confirm_delete_{item_id}"] = True
        with col_edit:
            if st.button(f"Edit {item_name}", key=f"edit_btn_{item_id}"):
                st.session_state[f"editing_{item_id}"] = True
        if st.session_state.get(f"confirm_delete_{item_id}"):
            st.warning(f"Are you sure you want to delete {item_name}?")
            col_yes, col_no = st.columns(2)
            with col_yes:
                if st.button("Yes, delete", key=f"confirm_yes_{item_id}"):
                    requests.delete(f"{API_URL}/items/{item_id}")
                    st.rerun()
            with col_no:
                if st.button("No, cancel", key=f"confirm_no_{item_id}"):
                    st.session_state[f"confirm_delete_{item_id}"] = False
                    st.rerun()
        if st.session_state.get(f"editing_{item_id}"):
            new_name = st.text_input("New Name", value=item_name, key=f"name_{item_id}")
            new_date = st.date_input("New Expiration Date", value=exp_date_obj, key=f"date_{item_id}")
            new_is_frozen = st.checkbox("Going to the freezer?", value=bool(is_frozen_val), key=f"frozen_{item_id}")
            new_quantity = st.number_input("Quantity", value=item_quantity, min_value=1, step=1, key=f"qty_{item_id}")
            new_notes = st.text_area("Notes", value=item_notes, key=f"notes_{item_id}")
            if st.button("Save", key=f"save_{item_id}"):
                requests.put(f"{API_URL}/items/{item_id}", json={
                    "name": new_name,
                    "expiration_date": str(new_date),
                    "is_frozen": new_is_frozen,
                    "notes": new_notes,
                    "quantity": int(new_quantity)
                })
                st.session_state[f"editing_{item_id}"] = False
                st.rerun()
        st.divider()

        # Separate frozen items from regular items (excluding last item)
        frozen_items = [i for i in remaining_items if i[4] == 1]
        regular_items = [i for i in remaining_items if i[4] == 0]

        # Display Frozen section
        if frozen_items:
            with st.expander("🔵 Frozen (" + str(len(frozen_items)) + " items)"):
                for item in frozen_items:
                    item_id = item[0]
                    item_name = item[1]
                    exp_date_text = item[2]
                    image_path = item[3]
                    is_frozen_val = item[4]
                    item_notes = item[5] if len(item) > 5 else ""
                    item_quantity = item[6] if len(item) > 6 else 1

                    exp_date_obj = datetime.strptime(exp_date_text, "%Y-%m-%d").date()
                    status = get_status(exp_date_obj)
                    formatted_date = exp_date_obj.strftime("%b %d, %Y")
                    countdown_text = days_remaining_text(exp_date_obj)

                    st.write(f"**{item_name}** ({item_quantity}) — {formatted_date} ({countdown_text})")
                    if status == "Expired":
                        st.markdown(f"**Status:** 🔴 {status}")
                    elif status == "Expiring Soon":
                        st.markdown(f"**Status:** 🟡 {status}")
                    else:
                        st.markdown(f"**Status:** 🟢 {status}")
                    if item_notes:
                        st.markdown(f"**Notes:** {item_notes}")
                    if image_path:
                        st.image(image_path, width=350)
                    col_delete, col_edit = st.columns(2)
                    with col_delete:
                        if st.button(f"Delete {item_name}", key=f"delete_{item_id}"):
                            st.session_state[f"confirm_delete_{item_id}"] = True
                    with col_edit:
                        if st.button(f"Edit {item_name}", key=f"edit_btn_{item_id}"):
                            st.session_state[f"editing_{item_id}"] = True
                    if st.session_state.get(f"confirm_delete_{item_id}"):
                        st.warning(f"Are you sure you want to delete {item_name}?")
                        col_yes, col_no = st.columns(2)
                        with col_yes:
                            if st.button("Yes, delete", key=f"confirm_yes_{item_id}"):
                                requests.delete(f"{API_URL}/items/{item_id}")
                                st.rerun()
                        with col_no:
                            if st.button("No, cancel", key=f"confirm_no_{item_id}"):
                                st.session_state[f"confirm_delete_{item_id}"] = False
                                st.rerun()
                    if st.session_state.get(f"editing_{item_id}"):
                        new_name = st.text_input("New Name", value=item_name, key=f"name_{item_id}")
                        new_date = st.date_input("New Expiration Date", value=exp_date_obj, key=f"date_{item_id}")
                        new_is_frozen = st.checkbox("Going to the freezer?", value=bool(is_frozen_val),
                                                    key=f"frozen_{item_id}")
                        new_quantity = st.number_input("Quantity", value=item_quantity, min_value=1, step=1,
                                                       key=f"qty_{item_id}")
                        new_notes = st.text_area("Notes", value=item_notes, key=f"notes_{item_id}")
                        if st.button("Save", key=f"save_{item_id}"):
                            requests.put(f"{API_URL}/items/{item_id}", json={
                                "name": new_name,
                                "expiration_date": str(new_date),
                                "is_frozen": new_is_frozen,
                                "notes": new_notes,
                                "quantity": int(new_quantity)
                            })
                            st.session_state[f"editing_{item_id}"] = False
                            st.rerun()
                    st.divider()

        # Display Regular items by status
        if regular_items:
            statuses = ["Expired", "Expiring Soon", "Fresh"]
            status_emojis = {"Expired": "🔴", "Expiring Soon": "🟡", "Fresh": "🟢"}
            for status_name in statuses:
                status_items = [i for i in regular_items if
                                get_status(datetime.strptime(i[2], "%Y-%m-%d").date()) == status_name]
                if not status_items:
                    continue
                with st.expander(f"{status_emojis[status_name]} {status_name} ({len(status_items)} items)"):
                    for item in status_items:
                        item_id = item[0]
                        item_name = item[1]
                        exp_date_text = item[2]
                        image_path = item[3]
                        is_frozen_val = item[4]
                        item_notes = item[5] if len(item) > 5 else ""
                        item_quantity = item[6] if len(item) > 6 else 1

                        exp_date_obj = datetime.strptime(exp_date_text, "%Y-%m-%d").date()
                        status = get_status(exp_date_obj)
                        formatted_date = exp_date_obj.strftime("%b %d, %Y")
                        countdown_text = days_remaining_text(exp_date_obj)

                        st.write(f"**{item_name}** ({item_quantity}) — {formatted_date} ({countdown_text})")
                        if status == "Expired":
                            st.markdown(f"**Status:** 🔴 {status}")
                        elif status == "Expiring Soon":
                            st.markdown(f"**Status:** 🟡 {status}")
                        else:
                            st.markdown(f"**Status:** 🟢 {status}")
                        if item_notes:
                            st.markdown(f"**Notes:** {item_notes}")
                        if image_path:
                            st.image(image_path, width=350)
                        col_delete, col_edit = st.columns(2)
                        with col_delete:
                            if st.button(f"Delete {item_name}", key=f"delete_{item_id}"):
                                st.session_state[f"confirm_delete_{item_id}"] = True
                        with col_edit:
                            if st.button(f"Edit {item_name}", key=f"edit_btn_{item_id}"):
                                st.session_state[f"editing_{item_id}"] = True
                        if st.session_state.get(f"confirm_delete_{item_id}"):
                            st.warning(f"Are you sure you want to delete {item_name}?")
                            col_yes, col_no = st.columns(2)
                            with col_yes:
                                if st.button("Yes, delete", key=f"confirm_yes_{item_id}"):
                                    requests.delete(f"{API_URL}/items/{item_id}")
                                    st.rerun()
                            with col_no:
                                if st.button("No, cancel", key=f"confirm_no_{item_id}"):
                                    st.session_state[f"confirm_delete_{item_id}"] = False
                                    st.rerun()
                        if st.session_state.get(f"editing_{item_id}"):
                            new_name = st.text_input("New Name", value=item_name, key=f"name_{item_id}")
                            new_date = st.date_input("New Expiration Date", value=exp_date_obj, key=f"date_{item_id}")
                            new_is_frozen = st.checkbox("Going to the freezer?", value=bool(is_frozen_val),
                                                        key=f"frozen_{item_id}")
                            new_quantity = st.number_input("Quantity", value=item_quantity, min_value=1, step=1,
                                                           key=f"qty_{item_id}")
                            new_notes = st.text_area("Notes", value=item_notes, key=f"notes_{item_id}")
                            if st.button("Save", key=f"save_{item_id}"):
                                requests.put(f"{API_URL}/items/{item_id}", json={
                                    "name": new_name,
                                    "expiration_date": str(new_date),
                                    "is_frozen": new_is_frozen,
                                    "notes": new_notes,
                                    "quantity": int(new_quantity)
                                })
                                st.session_state[f"editing_{item_id}"] = False
                                st.rerun()
                        st.divider()

    # Display Fresh Produce section
    if produce_items:
        with st.expander("🥬 Fresh Produce (" + str(len(produce_items)) + " items)"):
            for produce in produce_items:
                prod_id = produce[0]
                prod_name = produce[1]
                prod_ripeness = produce[2]
                prod_storage = produce[3]
                prod_notes = produce[4]
                prod_qty = produce[5]

                st.write(f"**{prod_name}** ({prod_qty}) — {prod_storage}")
                st.write(f"Ripeness: {prod_ripeness}")

                if prod_notes:
                    st.markdown(f"**Notes:** {prod_notes}")

                col_delete, col_edit = st.columns(2)

                with col_delete:
                    if st.button(f"Delete {prod_name}", key=f"delete_prod_{prod_id}"):
                        st.session_state[f"confirm_delete_prod_{prod_id}"] = True

                with col_edit:
                    if st.button(f"Edit {prod_name}", key=f"edit_prod_btn_{prod_id}"):
                        st.session_state[f"editing_prod_{prod_id}"] = True

                if st.session_state.get(f"confirm_delete_prod_{prod_id}"):
                    st.warning(f"Are you sure you want to delete {prod_name}?")
                    col_yes, col_no = st.columns(2)

                    with col_yes:
                        if st.button("Yes, delete", key=f"confirm_yes_prod_{prod_id}"):
                            requests.delete(f"{API_URL}/produce/{prod_id}")
                            st.rerun()

                    with col_no:
                        if st.button("No, cancel", key=f"confirm_no_prod_{prod_id}"):
                            st.session_state[f"confirm_delete_prod_{prod_id}"] = False
                            st.rerun()

                if st.session_state.get(f"editing_prod_{prod_id}"):
                    new_prod_name = st.text_input("Produce Name", value=prod_name, key=f"prod_name_{prod_id}")
                    new_ripeness = st.text_input("Ripeness", value=prod_ripeness, key=f"ripeness_{prod_id}")
                    new_storage = st.selectbox("Storage", ["Fridge", "Counter"],
                                               index=["Fridge", "Counter"].index(prod_storage),
                                               key=f"storage_{prod_id}")
                    new_prod_qty = st.number_input("Quantity", value=prod_qty, min_value=1, step=1,
                                                   key=f"prod_qty_{prod_id}")
                    new_prod_notes = st.text_area("Notes", value=prod_notes, key=f"prod_notes_{prod_id}")

                    if st.button("Save", key=f"save_prod_{prod_id}"):
                        requests.put(f"{API_URL}/produce/{prod_id}", json={
                            "name": new_prod_name,
                            "ripeness": new_ripeness,
                            "storage_location": new_storage,
                            "notes": new_prod_notes,
                            "quantity": int(new_prod_qty)
                        })
                        st.session_state[f"editing_prod_{prod_id}"] = False
                        st.rerun()

                st.divider()