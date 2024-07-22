from dataclasses import asdict
import json
import requests

from library.backend.api import BookService, UserService
from library.backend.api import NotFoundException, InvalidStateException
from library.backend.models import Book, User, LogEntry
from library.config import APP_CONFIG


class WebBookService(BookService):

    def __init__(self):
        self.url = APP_CONFIG.remote_backend()
    
    def getBook(self, isbn: str) -> Book:
        url = "%s/books/%s" % (self.url, isbn)
        resp = requests.get(url)
        if resp.status_code == 404:
            raise NotFoundException('No book in database with ISBN %s' % isbn)
        return Book(**json.loads(resp.text))

    def listBooks(self, search: str|None = None) -> list[Book]:
        url = "%s/books" % self.url
        params = {'query': search}
        resp = requests.get(url, params=params)
        return list(map(lambda r: Book(**r), json.loads(resp.text)))

    def listBooksByStatus(self, is_out) -> list[Book]:
        url ="%s/books" % self.url
        params = {'is_out': int(is_out)}
        resp = requests.get(url, params=params)
        return list(map(lambda r: Book(**r), json.loads(resp.text)))

    def createBook(self, book: Book):
        url = "%s/books" % self.url
        data = {'book': asdict(book)}
        requests.post(url, json=data)

    def checkoutBook(self, isbn: str, user: User):
        url = "%s/books/%s/checkout" % (self.url, isbn)
        data = {'user_id': user.user_id}
        resp = requests.post(url, json=data)
        if resp.status_code == 400:
            raise InvalidStateException('Book with ISBN %s already out' % isbn)

    def returnBook(self, isbn: str):
        url = "%s/books/%s/return" % (self.url, isbn)
        resp = requests.post(url)
        if resp.status_code == 400:
            raise InvalidStateException('Book with ISBN %s is not out' % isbn)

    def listBookCheckoutHistory(self, isbn: str) -> list[LogEntry]:
        pass

    def listUserCheckoutHistory(self, user_id: int) -> list[LogEntry]:
        pass

class WebUserService(UserService):

    def __init__(self):
        self.url = APP_CONFIG.remote_backend()

    def getUser(self, user_id: int) -> User:
        pass

    def createUser(self, name: str, email: str) -> User:
        pass

    def listUsers(self) -> list[User]:
        pass
