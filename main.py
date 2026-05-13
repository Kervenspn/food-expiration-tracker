from fastapi import FastAPI
from pydantic import BaseModel
from db import init_db, get_items, add_item, delete_item, update_item, get_produce, add_produce, delete_produce, update_produce
from camera import capture_image

app = FastAPI()
init_db()

class ItemCreate(BaseModel):
    name: str
    expiration_date: str
    image_path: str | None = None
    is_frozen: bool = False
    notes: str = ""
    quantity: int = 1

class ItemUpdate(BaseModel):
    name: str
    expiration_date: str
    is_frozen: bool = False
    notes: str = ""
    quantity: int = 1

class ProduceCreate(BaseModel):
    name: str
    ripeness: str
    storage_location: str = "Fridge"
    notes: str = ""
    quantity: int = 1
    image_path: str | None = None

class ProduceUpdate(BaseModel):
    name: str
    ripeness: str
    storage_location: str = "Fridge"
    notes: str = ""
    quantity: int = 1

@app.get("/")
def root():
    return {"message": "test"}

@app.get("/items")
def read_items():
    return get_items()

@app.post("/items")
def create_item(item: ItemCreate):
    add_item(item.name, item.expiration_date, item.image_path, item.is_frozen, item.notes, item.quantity)
    return {"message": "Item added"}

@app.delete("/items/{item_id}")
def remove_item(item_id: int):
    delete_item(item_id)
    return {"message": "Item deleted"}

@app.put("/items/{item_id}")
def edit_item(item_id: int, item: ItemUpdate):
    update_item(item_id, item.name, item.expiration_date, item.is_frozen, item.notes, item.quantity)
    return {"message": "Item updated"}

@app.get("/produce")
def read_produce():
    return get_produce()

@app.post("/produce")
def create_produce(produce: ProduceCreate):
    add_produce(produce.name, produce.ripeness, produce.storage_location, produce.notes, produce.quantity, produce.image_path)
    return {"message": "Produce added"}

@app.delete("/produce/{produce_id}")
def remove_produce(produce_id: int):
    delete_produce(produce_id)
    return {"message": "Produce deleted"}

@app.put("/produce/{produce_id}")
def edit_produce(produce_id: int, produce: ProduceUpdate):
    update_produce(produce_id, produce.name, produce.ripeness, produce.storage_location, produce.notes, produce.quantity)
    return {"message": "Produce updated"}

@app.post("/capture")
def capture_item():
    image_path = capture_image()
    if image_path is None:
        return {"error": "Camera failed"}
    return {"image_path": image_path}