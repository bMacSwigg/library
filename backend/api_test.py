import unittest
import time

from backend.api import BookService, InvalidStateException, NotFoundException
from backend.db import Action, Database
from backend.models import Book, User
from backend.testbase import BaseTestCase
from notifs.mailgun_client import FakeEmail

class TestBookService(BaseTestCase):

    TEST_DATABASE = ':memory:'

    def setUp(self):
        self.books = BookService()
        self.books.db = Database(self.TEST_DATABASE)
        self.books.email = FakeEmail()
        with open('books.schema', 'r') as file:
            schema = file.read()
            self.books.db.con.cursor().executescript(schema)

    def test_getBook_exists(self):
        self.books.db.putBook('isbn1', 'title', 'author', 'cat', 'year', 'img')

        book = self.books.getBook('isbn1')

        self.assertEqual(book.isbn, 'isbn1')
        self.assertEqual(book.title, 'title')
        self.assertEqual(book.author, 'author')
        self.assertEqual(book.category, 'cat')
        self.assertEqual(book.year, 'year')
        self.assertEqual(book.thumbnail, 'img')

    def test_getBook_setsDefaultLogVals(self):
        self.books.db.putBook('isbn1', 'title', 'author', 'cat', 'year', 'img')

        book = self.books.getBook('isbn1')

        self.assertEqual(book.is_out, False)
        self.assertEqual(book.checkout_user, '')
        self.assertEqual(book.checkout_time, '')

    def test_getBook_setsCheckoutLogVals(self):
        self.books.db.putBook('isbn1', 'title', 'author', 'cat', 'year', 'img')
        self.books.db.putUser(1234, 'somebody', 'test@example.com')
        self.books.db.putLog('isbn1', Action.CHECKOUT, 1234)

        book = self.books.getBook('isbn1')

        self.assertEqual(book.is_out, True)
        self.assertEqual(book.checkout_user, 'somebody')
        self.assertAboutNow(book.checkout_time)

    def test_getBook_setsReturnLogVals(self):
        self.books.db.putBook('isbn1', 'title', 'author', 'cat', 'year', 'img')
        self.books.db.putLog('isbn1', Action.RETURN)

        book = self.books.getBook('isbn1')

        self.assertEqual(book.is_out, False)
        self.assertEqual(book.checkout_user, '')
        self.assertEqual(book.checkout_time, '')

    def test_getBook_setsCreateLogVals(self):
        self.books.db.putBook('isbn1', 'title', 'author', 'cat', 'year', 'img')
        self.books.db.putLog('isbn1', Action.CREATE)

        book = self.books.getBook('isbn1')

        self.assertEqual(book.is_out, False)
        self.assertEqual(book.checkout_user, '')
        self.assertEqual(book.checkout_time, '')

    def test_getBook_doesNotExist(self):
        with self.assertRaises(NotFoundException):
            self.books.getBook('isbn1')

    def test_listBooks(self):
        self.books.db.putBook('isbn1', 'Babel', 'R.F. Kuang', 'Fiction', '2022', 'url')
        self.books.db.putBook('isbn2', 'Looking For Alaska', 'John Green', 'Fiction', '2005', 'url')

        books = self.books.listBooks()

        self.assertEqual(books[0].isbn, 'isbn1')
        self.assertEqual(books[0].title, 'Babel')
        self.assertEqual(books[0].author, 'R.F. Kuang')
        self.assertEqual(books[0].category, 'Fiction')
        self.assertEqual(books[0].year, '2022')
        self.assertEqual(books[0].thumbnail, 'url')
        self.assertEqual(books[1].isbn, 'isbn2')
        self.assertEqual(books[1].title, 'Looking For Alaska')
        self.assertEqual(books[1].author, 'John Green')
        self.assertEqual(books[1].category, 'Fiction')
        self.assertEqual(books[1].year, '2005')
        self.assertEqual(books[1].thumbnail, 'url')

    def test_listBooks_setsLogValues(self):
        self.books.db.putUser(1234, 'somebody', 'test@example.com')
        self.books.db.putBook('isbn1', '', '', '', '', '')
        self.books.db.putBook('isbn2', '', '', '', '', '')
        self.books.db.putLog('isbn1', Action.CREATE)
        self.books.db.putLog('isbn2', Action.CREATE)
        time.sleep(1)
        self.books.db.putLog('isbn1', Action.CHECKOUT, 1234)

        books = self.books.listBooks()

        self.assertEqual(books[0].isbn, 'isbn1')
        self.assertEqual(books[0].is_out, True)
        self.assertEqual(books[0].checkout_user, 'somebody')
        self.assertAboutNow(books[0].checkout_time)
        self.assertEqual(books[1].isbn, 'isbn2')
        self.assertEqual(books[1].is_out, False)
        self.assertEqual(books[1].checkout_user, '')
        self.assertEqual(books[1].checkout_time, '')

    def test_listBooks_withSearch(self):
        self.books.db.putBook('isbn1', 'Babel', 'R.F. Kuang', 'Fiction', '2022', 'url')
        self.books.db.putBook('isbn2', 'Looking For Alaska', 'John Green', 'Fiction', '2005', 'url')

        books = self.books.listBooks('looking')

        self.assertEqual(len(books), 1)
        self.assertEqual(books[0].isbn, 'isbn2')
        self.assertEqual(books[0].title, 'Looking For Alaska')

    def test_listBooksByStatus_checkedOut(self):
        self.books.db.putUser(1234, 'somebody', 'test@example.com')
        self.books.db.putBook('isbn-in', '', '', '', '', '')
        self.books.db.putBook('isbn-out', '', '', '', '', '')
        self.books.db.putLog('isbn-in', Action.CREATE)
        self.books.db.putLog('isbn-out', Action.CHECKOUT, 1234)

        books = self.books.listBooksByStatus(True)

        self.assertEqual(len(books), 1)
        self.assertEqual(books[0].isbn, 'isbn-out')

    def test_listBooksByStatus_checkedIn(self):
        self.books.db.putUser(1234, 'somebody', 'test@example.com')
        self.books.db.putBook('isbn-in', '', '', '', '', '')
        self.books.db.putBook('isbn-out', '', '', '', '', '')
        self.books.db.putLog('isbn-in', Action.CREATE)
        self.books.db.putLog('isbn-out', Action.CHECKOUT, 1234)

        books = self.books.listBooksByStatus(False)

        self.assertEqual(len(books), 1)
        self.assertEqual(books[0].isbn, 'isbn-in')
        
    def test_createBook(self):
        book = Book('isbn1', 'Paul', 'Andrea Lawler', 'Fiction', '2017', 'url')

        self.books.createBook(book)
        res = self.books.getBook('isbn1')

        self.assertEqual(res, book)

    def test_checkoutBook(self):
        book = Book('isbn1', '', '', '', '', '')
        self.books.createBook(book)
        user = User(1234, 'user', 'user@example.com')
        self.books.db.putUser(user.user_id, user.name, user.email)
        time.sleep(1)
        self.books.checkoutBook('isbn1', user)

        res = self.books.getBook('isbn1')

        self.assertEqual(res.is_out, True)
        self.assertEqual(res.checkout_user, 'user')
        self.assertAboutNow(res.checkout_time)

    def test_checkoutBook_alreadyOut(self):
        book = Book('isbn1', '', '', '', '', '')
        self.books.createBook(book)
        user = User(1234, 'user', 'user@example.com')
        self.books.db.putUser(user.user_id, user.name, user.email)
        time.sleep(1)
        self.books.checkoutBook('isbn1', user)

        with self.assertRaises(InvalidStateException):
            self.books.checkoutBook('isbn1', user)

    def test_checkoutBook_sendsEmail(self):
        # TODO
        return

    def test_returnBook(self):
        book = Book('isbn1', '', '', '', '', '')
        self.books.createBook(book)
        user = User(1234, 'user', 'user@example.com')
        self.books.db.putUser(user.user_id, user.name, user.email)
        time.sleep(1)
        self.books.checkoutBook('isbn1', user)
        time.sleep(1)
        self.books.returnBook('isbn1')

        res = self.books.getBook('isbn1')

        self.assertEqual(res.is_out, False)
        self.assertEqual(res.checkout_user, '')
        self.assertEqual(res.checkout_time, '')

    def test_returnBook_notOut(self):
        book = Book('isbn1', '', '', '', '', '')
        self.books.createBook(book)

        with self.assertRaises(InvalidStateException):
            self.books.returnBook('isbn1')

    def test_returnBook_sendsEmail(self):
        # TODO
        return

    def test_listBookCheckoutHistory(self):
        self.books.createBook(Book('isbn1', '', '', '', '', ''))
        self.books.createBook(Book('isbn2', '', '', '', '', ''))
        user = User(1234, 'user', 'user@example.com')
        self.books.db.putUser(user.user_id, user.name, user.email)
        time.sleep(1)
        self.books.checkoutBook('isbn1', user)
        time.sleep(1)
        self.books.returnBook('isbn1')
        self.books.checkoutBook('isbn2', user)

        res = self.books.listBookCheckoutHistory('isbn1')

        self.assertEqual(len(res), 2)
        self.assertEqual(res[0][0], Action.CHECKOUT.value)
        self.assertEqual(res[0][1], 'user')
        self.assertAboutNow(res[0][2])
        self.assertEqual(res[1][0], Action.RETURN.value)
        self.assertEqual(res[1][1], '')
        self.assertAboutNow(res[1][2])

    def test_getUser(self):
        self.books.db.putUser(1234, 'Brian', 'me@example.com')

        res = self.books.getUser(1234)

        self.assertEqual(res.user_id, 1234)
        self.assertEqual(res.name, 'Brian')
        self.assertEqual(res.email, 'me@example.com')

    def test_createUser(self):
        user = User(1234, 'Brian', 'me@example.com')

        self.books.createUser(user)
        res = self.books.getUser(1234)

        self.assertEqual(res, user)

    def test_listUsers(self):
        self.books.db.putUser(1234, 'Brian', 'me@example.com')
        self.books.db.putUser(5678, 'Other', 'someone@example.com')

        res = self.books.listUsers()

        self.assertEqual(len(res), 2)
        self.assertEqual(res[0].user_id, 1234)
        self.assertEqual(res[0].name, 'Brian')
        self.assertEqual(res[0].email, 'me@example.com')
        self.assertEqual(res[1].user_id, 5678)
        self.assertEqual(res[1].name, 'Other')
        self.assertEqual(res[1].email, 'someone@example.com')


if __name__ == '__main__':
    unittest.main()
