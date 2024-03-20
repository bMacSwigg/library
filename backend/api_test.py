import unittest
import time

from backend.api import BookService
from backend.db import Action, Database
from backend.models import Book
from backend.testbase import BaseTestCase

class TestBookService(BaseTestCase):

    TEST_DATABASE = ':memory:'

    def setUp(self):
        self.books = BookService()
        self.books.db = Database(self.TEST_DATABASE)
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
        self.books.db.putLog('isbn1', Action.CHECKOUT, 'somebody')

        book = self.books.getBook('isbn1')

        self.assertEqual(book.is_out, True)
        self.assertEqual(book.checkout_user, 'somebody')
        self.assertAboutNow(book.checkout_time)

    def test_getBook_setsReturnLogVals(self):
        self.books.db.putBook('isbn1', 'title', 'author', 'cat', 'year', 'img')
        self.books.db.putLog('isbn1', Action.RETURN, 'somebody')

        book = self.books.getBook('isbn1')

        self.assertEqual(book.is_out, False)
        self.assertEqual(book.checkout_user, '')
        self.assertEqual(book.checkout_time, '')

    def test_getBook_setsCreateLogVals(self):
        self.books.db.putBook('isbn1', 'title', 'author', 'cat', 'year', 'img')
        self.books.db.putLog('isbn1', Action.CREATE, 'somebody')

        book = self.books.getBook('isbn1')

        self.assertEqual(book.is_out, False)
        self.assertEqual(book.checkout_user, '')
        self.assertEqual(book.checkout_time, '')

    def test_getBook_doesNotExist(self):
        with self.assertRaises(TypeError):
            # Not ideal error handling, but at least it's tested? lol
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
        self.books.db.putBook('isbn1', '', '', '', '', '')
        self.books.db.putBook('isbn2', '', '', '', '', '')
        self.books.db.putLog('isbn1', Action.CREATE, '')
        self.books.db.putLog('isbn2', Action.CREATE, '')
        time.sleep(1)
        self.books.db.putLog('isbn1', Action.CHECKOUT, 'somebody')

        books = self.books.listBooks()

        self.assertEqual(books[0].isbn, 'isbn1')
        self.assertEqual(books[0].is_out, True)
        self.assertEqual(books[0].checkout_user, 'somebody')
        self.assertAboutNow(books[0].checkout_time)
        self.assertEqual(books[1].isbn, 'isbn2')
        self.assertEqual(books[1].is_out, False)
        self.assertEqual(books[1].checkout_user, '')
        self.assertEqual(books[1].checkout_time, '')

    def test_createBook(self):
        book = Book('isbn1', 'Paul', 'Andrea Lawler', 'Fiction', '2017', 'url')

        self.books.createBook(book)
        res = self.books.getBook('isbn1')

        self.assertEqual(res, book)

    def test_checkoutBook(self):
        book = Book('isbn1', '', '', '', '', '')
        self.books.createBook(book)
        time.sleep(1)
        self.books.checkoutBook('isbn1', 'user')

        res = self.books.getBook('isbn1')

        self.assertEqual(res.is_out, True)
        self.assertEqual(res.checkout_user, 'user')
        self.assertAboutNow(res.checkout_time)

    def test_returnBook(self):
        book = Book('isbn1', '', '', '', '', '')
        self.books.createBook(book)
        time.sleep(1)
        self.books.checkoutBook('isbn1', 'user')
        time.sleep(1)
        self.books.returnBook('isbn1')

        res = self.books.getBook('isbn1')

        self.assertEqual(res.is_out, False)
        self.assertEqual(res.checkout_user, '')
        self.assertEqual(res.checkout_time, '')


if __name__ == '__main__':
    unittest.main()
