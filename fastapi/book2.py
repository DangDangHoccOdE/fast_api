from smtplib import bCRLF
from typing import Optional

from fastapi import FastAPI,Body, Path, Query,HTTPException
from pydantic import BaseModel, Field
from starlette import status

app = FastAPI()

class Book:
    id:int
    title:str
    author:str
    description:str
    rating:int
    published_date: int

    def __init__(self, id, title, author, description, rating, published_date):
        self.id = id
        self.title = title
        self.author = author
        self.rating = rating
        self.description = description
        self.published_date = published_date

class BookRequest(BaseModel):
    id: Optional[int] = Field(description="Id is not needed on create",default=None)
    title: str = Field(min_length= 3)
    author: str = Field(min_length= 1)
    description: str = Field(min_length= 1 , max_length=100)
    rating: int = Field(gt=-1, lt=6)
    published_date: int = Field(gt=1999, lt=2024)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "A new book",
                "author": "codingwithDangbaby",
                "description":"A new description of a book",
                "rating" : 5,
                "published_date":2029
            }
        }
    }

BOOKS = [
    Book(1, 'Computer science pro', 'codingwithroby','A very nice book',5,2018),
    Book(2, 'Sach 2', 'tac gia 2','A very nice book',5,2017),
    Book(3, 'Sach 3', 'tac gia 3','A very nice book 3',3,2016),
    Book(4, 'Sach 4', 'tac gia 4','A very nice book 4',4,2015),
    Book(5, 'Sach 5', 'tac gia 5','A very nice book 5',5,2020),
]

@app.get("/books/publish/")
async def read_book_by_published_date(published_date:int = Query(gt = 1999, lt = 2033)):
    books_to_return = []
    for book in BOOKS:
        if book.published_date == published_date:
            books_to_return.append(book)
    return books_to_return

@app.get("/books",status_code=status.HTTP_200_OK)
async def read_all_books():
    return BOOKS

@app.get("/books/{book_id}",status_code=status.HTTP_200_OK)
async def read_book(book_id:int = Path(gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="NOT FOUND")

@app.put("/books/update_book",status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book : BookRequest):
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book.id:
            BOOKS[i] = book
            book_changed = True
    if not book_changed:
        raise HTTPException(status_code=404, detail="NOT FOUND")

@app.get("/books/",status_code=status.HTTP_200_OK)
async def read_book_by_rating(book_rating: int = Query(gt =0 , lt =6)):
    books_to_return = []
    for book in BOOKS:
        if book.rating == book_rating:
            books_to_return.append(book)
    return books_to_return

@app.delete("/books/{book_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(gt=0)):
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            book_changed = True
            break
    if not book_changed:
        raise HTTPException(status_code=404, detail="NOT FOUND")

@app.post("/create-book",status_code=status.HTTP_201_CREATED)
async def create_book(book_request : BookRequest):
    new_book = Book(**book_request.model_dump())
    # Phương thức model_dump dùng để chuyển book_request thành từ đin có key và value
    # Dấu ** Dùng từ điển vừa tạo để thành 1 đối tương book
    BOOKS.append(find_book_id(new_book))

def find_book_id(book: Book):
    if len(BOOKS) > 0 :
        book.id = BOOKS[-1].id + 1
    else:
        book.id = 1
    return book