import json
from urllib.request import urlopen

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

class LookupService:

    GOOGLE_BOOKS_ENDPOINT = 'https://www.googleapis.com/books/v1/volumes?q=isbn:%s'

    def lookupIsbn(self, isbn: str) -> Book:
        res = json.load(urlopen(self.GOOGLE_BOOKS_ENDPOINT % isbn))
        vals = res['items'][0]['volumeInfo']
        title = vals['title']
        author = ', '.join(vals['authors'])
        print(self._extractVal(vals, 'mainCategory'))
        print(self._extractVal(vals, 'categories'))
        print(self._extractVal(vals, 'publishedDate'))
        # Also imageLinks.thumbnail
        return Book(isbn, title, author)

    def _extractVal(self, vals, name):
        return vals[name] if name in vals else ''

ls = LookupService()
print(ls.lookupIsbn('9781398515697'))
print(ls.lookupIsbn('9780060853983'))
        
