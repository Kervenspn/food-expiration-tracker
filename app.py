import os
import uuid
import requests
import streamlit as st
from datetime import date, datetime
from PIL import Image
from streamlit_cropper import st_cropper

API_URL = "http://127.0.0.1:8000"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

st.title("Food Expiration Tracker")

def get_status(exp_date):
    today = date.today()

    if exp_date < today:
        return "Expired"
    elif (exp_date - today).days <= 3:
        return "Expiring Soon"
    else:
        return "Fresh"

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

st.header("Add Food Item")

name = st.text_input("Food Name")
exp_date = st.date_input("Expiration Date", value=date.today())

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

if st.button("Add Item"):
    if name:
        image_path = None

        if cropped_image is not None:
            image_path = save_cropped_image(cropped_image)

        requests.post(f"{API_URL}/items", json={
            "name": name,
            "expiration_date": str(exp_date),
            "image_path": image_path
        })

        if "selected_image_path" in st.session_state:
            del st.session_state["selected_image_path"]

        st.success("Item added")
        st.rerun()
    else:
        st.warning("Enter a name")

st.header("Your Items")

response = requests.get(f"{API_URL}/items")
items = response.json()

if not items:
    st.info("No items added yet.")
else:
    for item in items:
        item_id = item[0]
        item_name = item[1]
        exp_date_text = item[2]
        image_path = item[3]

        exp_date_obj = datetime.strptime(exp_date_text, "%Y-%m-%d").date()
        status = get_status(exp_date_obj)
        formatted_date = exp_date_obj.strftime("%B %d, %Y")

        st.subheader(item_name)
        st.write(f"Expiration: {formatted_date}")
        st.write(f"Status: {status}")

        if image_path:
            st.image(image_path, width=350)

        if st.button(f"Delete {item_name}", key=f"delete_{item_id}"):
            requests.delete(f"{API_URL}/items/{item_id}")
            st.rerun()

        st.divider()