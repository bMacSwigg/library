import json
from urllib.request import urlopen

from library.backend.api import BookService, UserService
from library.backend.api import NotFoundException, InvalidStateException
from library.backend.models import Book, User, LogEntry
from library.config import APP_CONFIG


class WebBookService(BookService):

    def __init__(self):
        self.url = APP_CONFIG.remote_backend()
    
    def getBook(self, isbn: str) -> Book:
        pass

    def listBooks(self, search: str|None = None) -> list[Book]:
        pass

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
