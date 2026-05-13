from fastapi import FastAPI
from pydantic import BaseModel
from db import init_db, get_items, add_item, delete_item, update_item
from camera import capture_image

app = FastAPI()
init_db()

# Model for adding a new item
class ItemCreate(BaseModel):
    name: str
    expiration_date: str
    image_path: str | None = None
    category: str = "Fridge"

# Model for editing an existing item
class ItemUpdate(BaseModel):
    name: str
    expiration_date: str
    category: str = "Fridge"

@app.get("/")
def root():
    return {"message": "test"}

@app.get("/items")
def read_items():
    return get_items()

@app.post("/items")
def create_item(item: ItemCreate):
    add_item(item.name, item.expiration_date, item.image_path, item.category)
    return {"message": "Item added"}

@app.post("/capture")
def capture_item():
    image_path = capture_image()

    if image_path is None:
        return {"error": "Camera failed"}

    return {"image_path": image_path}

@app.delete("/items/{item_id}")
def remove_item(item_id: int):
    delete_item(item_id)
    return {"message": "Item deleted"}

@app.put("/items/{item_id}")
def edit_item(item_id: int, item: ItemUpdate):
    update_item(item_id, item.name, item.expiration_date, item.category)
    return {"message": "Item updated"}