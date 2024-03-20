import json
from urllib.request import urlopen

from backend.models import Book
from backend.db import Action, Database
from constants import *


class NotFoundException(Exception):

    def __init__(self, message = ''):
        self.message = message
        super().__init__(self.message)

class BookService:

    def __init__(self):
        self.db = Database(DB_FILE)

    def _bookFromTuple(self, book_vals: tuple, log_vals: tuple) -> Book:
        is_out = (log_vals[2] == Action.CHECKOUT.value)
        checkout_user = (log_vals[3] if is_out else '')
        checkout_time = (log_vals[1] if is_out else '')
        return Book(book_vals[0], book_vals[1], book_vals[2],
                    book_vals[3], book_vals[4], book_vals[5],
                    is_out, checkout_user, checkout_time)

    def getBook(self, isbn: str) -> Book:
        book_vals = self.db.getBook(isbn)
        if book_vals is None:
            raise NotFoundException('No book in database with ISBN %s' % isbn)
        log_vals = self.db.getLatestLog(isbn)
        return self._bookFromTuple(book_vals, log_vals)

    def listBooks(self) -> list[Book]:
        vals = self.db.listBooks()
        # It would probably be more efficient to do this with a JOIN in the DB
        # query. But this is simpler, and the scale of data is too small to matter.
        return [self._bookFromTuple(book_vals, self.db.getLatestLog(book_vals[0]))
                for book_vals in vals]

    def createBook(self, book: Book):
        self.db.putBook(book.isbn, book.title, book.author,
                        book.category, book.year, book.thumbnail)
        self.db.putLog(book.isbn, Action.CREATE, '')

    # TODO: Should these validate the current state of the book?
    def checkoutBook(self, isbn, user):
        self.db.putLog(isbn, Action.CHECKOUT, user)

    def returnBook(self, isbn):
        self.db.putLog(isbn, Action.RETURN, '')


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
