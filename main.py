from fastapi import FastAPI
from pydantic import BaseModel
from db import init_db, get_items, add_item, delete_item
from camera import capture_image

app = FastAPI()
init_db()

class ItemCreate(BaseModel):
    name: str
    expiration_date: str
    image_path: str | None = None

@app.get("/")
def root():
    return {"message": "test"}

@app.get("/items")
def read_items():
    return get_items()

@app.post("/items")
def create_item(item: ItemCreate):
    add_item(item.name, item.expiration_date, item.image_path)
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