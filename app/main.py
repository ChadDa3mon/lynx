from fastapi import FastAPI
from pydantic import BaseModel
from models import Bookmark
from typing import Dict


bookmarks = []

app = FastAPI()

@app.get("/bookmarks")
async def get_bookmarks():
    return bookmarks

@app.post("/bookmarks/add")
async def add_bookmark(payload: Dict[str, str]):
    url = payload.get("URL")
    body = payload.get("BODY")

    # Perform further processing or validation as needed

    # Example: Creating a new bookmark
    bookmark = Bookmark(id=len(bookmarks) + 1, title="", url=url)
    bookmarks.append(bookmark)
    print(f"URL: {url}")
    print(f"Body: {body}")

    return {"message": "Bookmark added successfully"}



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
