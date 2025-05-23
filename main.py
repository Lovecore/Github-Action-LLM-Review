from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="Simple FastAPI Example",
    description="A basic FastAPI application for GitHub Actions testing",
    version="0.1.0"
)

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

# In-memory storage
items_db = {}

@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI example application!"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item_id": item_id, "item": items_db[item_id]}

@app.post("/items/")
async def create_item(item: Item):
    item_id = len(items_db) + 1
    items_db[item_id] = item.dict()
    return {"item_id": item_id, "item": item.dict()}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/hello")
async def hello():
    return {"message": "Hello, World!"}

@app.get("/hello/{name}")
async def hello_name(name: str):
    return {"message": f"Hello, {name}!"}

@app.get("/vulnerable")
async def vulnerable():
    return {"message": "This is a vulnerable endpoint!"}

@app.get("/vulnerable/{name}")
async def vulnerable_name(name: str):
    return {"message": f"Hello, {name}!"}
