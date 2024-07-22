from dataclasses import asdict
import json
import requests
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen
# TODO: switch to requests library

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
        pass

    def createBook(self, book: Book):
        pass

    def checkoutBook(self, isbn: str, user: User):
        pass

    def returnBook(self, isbn: str):
        pass

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
