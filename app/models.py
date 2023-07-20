from pydantic import BaseModel

class Bookmark(BaseModel):
    id: int
    title: str
    url: str
