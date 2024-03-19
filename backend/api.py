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
        return Book(vals[0], vals[1], vals[2], vals[3], vals[4], vals[5])

    def getBook(self, isbn: str) -> Book:
        vals = self.db.getBook(isbn)
        return self._bookFromTuple(vals)

    def listBooks(self) -> list[Book]:
        vals = self.db.listBooks()
        return [self._bookFromTuple(val) for val in vals]

    def createBook(self, book: Book):
        self.db.putBook(book.isbn, book.title, book.author,
                        book.category, book.year, book.thumbnail)
        

class LookupService:

    GOOGLE_BOOKS_ENDPOINT = 'https://www.googleapis.com/books/v1/volumes?q=isbn:%s'

    def lookupIsbn(self, isbn: str) -> Book:
        res = json.load(urlopen(self.GOOGLE_BOOKS_ENDPOINT % isbn))
        vals = res['items'][0]['volumeInfo']
        title = vals['title'] if 'title' in vals else ''
        authors = vals['authors'] if 'authors' in vals else []
        author = ', '.join(authors)
        if 'mainCategory' in vals:
            category = vals['mainCategory']
        elif 'categories' in vals and len(vals['categories']) > 0:
            category = vals['categories'][0]
        else:
            category = ''
        year = vals['publishedDate'][:4] if 'publishedDate' in vals else ''
        thumbnail = vals['imageLinks']['thumbnail']  # Too annoying to do safely
        return Book(isbn, title, author, category, year, thumbnail)
