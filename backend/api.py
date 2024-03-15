from models import Book
from db import Database

class BookService:

    DB_FILE = 'books.db'

    def __init__(self):
        self.db = Database(self.DB_FILE)

    def getBook(self, isbn: str) -> Book:
        vals = self.db.get(isbn)
        return Book(vals[0], vals[1], vals[2])

    def listBooks(self) -> list[Book]:
        pass

    def importBook(self, isbn: str):
        # TODO: look up ISBN for metadata
        self.db.put(isbn, 'filler-title')

