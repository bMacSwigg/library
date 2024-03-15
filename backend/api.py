from backend.models import Book
from backend.db import Database

class BookService:

    # TODO: Move this into a settings file or something
    DB_FILE = 'C:\\Users\\User\\Documents\\GitHub\\library\\backend\\books.db'

    def __init__(self):
        self.db = Database(self.DB_FILE)

    def _bookFromTuple(self, vals: tuple) -> Book:
        return Book(vals[0], vals[1], vals[2])

    def getBook(self, isbn: str) -> Book:
        vals = self.db.get(isbn)
        return self._bookFromTuple(vals)

    def listBooks(self) -> list[Book]:
        vals = self.db.list()
        return [self._bookFromTuple(val) for val in vals]

    def createBook(self, book: Book):
        self.db.put(book.isbn, book.title, book.author)

