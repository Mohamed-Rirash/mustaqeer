from sqlalchemy.future import select
from fastapi import APIRouter
from app.config.dependencies import db_dependency
from app.schemas.test import BookCreate

from app.models.test import Book

test_router =APIRouter(
    tags=["test"],
)
@test_router.post("/books/", )
async def create_book(db: db_dependency, book:BookCreate):
    new_book = Book(**book.dict())
    print(new_book)
    db.add(new_book)
    await db.commit()
    await db.refresh(new_book)

    return {"message": "Book added successfully", "book": book}

@test_router.get("/books/")
async def get_books(db: db_dependency):
    result = await db.execute(select(Book))
    books = result.scalars().all()
    return books
