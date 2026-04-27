import streamlit as st
from datetime import date

st.title("Food Expiration Tracker")

if "items" not in st.session_state:
    st.session_state["items"] = []

def get_status(exp_date):
    today = date.today()

    if exp_date < today:
        return "Expired"
    elif (exp_date - today).days <= 3:
        return "Expiring Soon"
    else:
        return "Fresh"

st.header("Add Food Item")

name = st.text_input("Food Name")
exp_date = st.date_input("Expiration Date", value=date.today())
image = st.file_uploader("Upload Image (optional)", type=["png", "jpg", "jpeg"])

if st.button("Add Item"):
    if name:
        st.session_state["items"].append({
            "name": name,
            "exp": exp_date,
            "image": image
        })
        st.success("Item added")
    else:
        st.warning("Enter a name")

st.header("Your Items")

sorted_items = sorted(st.session_state["items"], key=lambda item: item["exp"])

if not sorted_items:
    st.info("No items added yet.")
else:
    for i, item in enumerate(sorted_items):
        status = get_status(item["exp"])
        formatted_date = item["exp"].strftime("%B %d, %Y")

        st.subheader(item["name"])
        st.write(f"Expiration: {formatted_date}")
        st.write(f"Status: {status}")

        if item["image"]:
            st.image(item["image"], width=150)

        if st.button(f"Delete {item['name']}", key=f"delete_{i}"):
            st.session_state["items"].remove(item)
            st.rerun()

        st.divider()