import json
from urllib.request import urlopen

from backend.models import Book, User
from backend.db import Action, Database
from constants import *
from notifs.mailgun_client import Email


class NotFoundException(Exception):

    def __init__(self, message = ''):
        self.message = message
        super().__init__(self.message)


class InvalidStateException(Exception):

    def __init__(self, message = ''):
        self.message = message
        super().__init__(self.message)


class BookService:

    def __init__(self):
        self.db = Database(DB_FILE)
        self.email = Email()

    def _parseLogs(self, log_vals: tuple) -> tuple[str, str]:
        user_id = log_vals[4]
        user = (
            self.db.getUser(user_id)[1]
            if user_id
            else log_vals[3]
        )
        time = log_vals[1]
        return user, time

    def _bookFromTuple(self, book_vals: tuple, log_vals: tuple) -> Book:
        is_out = (log_vals[2] == Action.CHECKOUT.value)
        if is_out:
            checkout_user, checkout_time = self._parseLogs(log_vals)
        else:
            (checkout_user, checkout_time) = ('', '')

        return Book(book_vals[0], book_vals[1], book_vals[2],
                    book_vals[3], book_vals[4], book_vals[5],
                    is_out, checkout_user, checkout_time)

    def getBook(self, isbn: str) -> Book:
        book_vals = self.db.getBook(isbn)
        if book_vals is None:
            raise NotFoundException('No book in database with ISBN %s' % isbn)
        log_vals = self.db.getLatestLog(isbn)
        return self._bookFromTuple(book_vals, log_vals)

    def listBooks(self, search: str|None = None) -> list[Book]:
        vals = self.db.listBooks(search)
        # It would probably be more efficient to do this with a JOIN in the DB
        # query. But this is simpler, and the scale of data is too small to matter.
        return [self._bookFromTuple(book_vals, self.db.getLatestLog(book_vals[0]))
                for book_vals in vals]

    # Lists all checked-out or checked-in books
    def listBooksByStatus(self, is_out) -> list[Book]:
        allBooks = self.listBooks()
        return [b for b in allBooks if b.is_out == is_out]

    def createBook(self, book: Book):
        self.db.putBook(book.isbn, book.title, book.author,
                        book.category, book.year, book.thumbnail)
        self.db.putLog(book.isbn, Action.CREATE)

    def checkoutBook(self, isbn: str, user: User):
        prev_log = self.db.getLatestLog(isbn)
        if prev_log[2] == Action.CHECKOUT.value:
            raise InvalidStateException('Book with ISBN %s already out' % isbn)

        self.db.putLog(isbn, Action.CHECKOUT, user.user_id)

        book = self.getBook(isbn)
        self.email.send_checkout_message(book, user)

    def returnBook(self, isbn):
        checkout_log = self.db.getLatestLog(isbn)
        if checkout_log[2] != Action.CHECKOUT.value:
            raise InvalidStateException('Book with ISBN %s is not out' % isbn)

        self.db.putLog(isbn, Action.RETURN)

        if not checkout_log[4]:
            # no user ID means no email to notify
            return
        book = self.getBook(isbn)
        user_vals = self.db.getUser(checkout_log[4])
        user = User(user_vals[0], user_vals[1], user_vals[2])
        ret_time = self.db.getLatestLog(isbn)[1]
        self.email.send_return_message(book, user, ret_time)
        

    def listBookCheckoutHistory(self, isbn) -> list[tuple[int, str, str]]:
        logs = self.db.listLogs(isbn)
        logs = filter(lambda l: l[2] in [Action.CHECKOUT.value, Action.RETURN.value], logs)
        logs = map(lambda l: (l[2],) + self._parseLogs(l), logs)
        return list(logs)

    def createUser(self, user: User):
        self.db.putUser(user.user_id, user.name, user.email)

    def listUsers(self):
        vals = self.db.listUsers()
        return [User(v[0], v[1], v[2]) for v in vals]


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
        if 'imageLinks' in vals and 'thumbnail' in vals['imageLinks']:
            thumbnail = vals['imageLinks']['thumbnail']
        else:
            thumbnail = ''
        return Book(isbn, title, author, category, year, thumbnail)
