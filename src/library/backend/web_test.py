from flask.testing import FlaskClient
import json
import os
import time
import unittest
from unittest import mock
from urllib.parse import urlencode
from werkzeug.test import TestResponse

from library.backend.api import NotFoundException, InvalidStateException
from library.backend.db import Database
from library.backend.models import Book, User, Action
from library.backend.testbase import BaseTestCase
from library.backend.web import WebBookService
from library.config import APP_CONFIG
from server.app import app

# sqlite doesn't seem to do a good job of wiping in-memory DBs
DB_NAME = __name__ + str(int(time.time()))
DB_FILE = "file:%s?mode=memory&cache=shared" % DB_NAME
print("using DB file '%s'" % DB_FILE)


class TestClientWrapper:
    def __init__(self, tc: FlaskClient):
        self.tc = tc

    # returns a TestResponse, duck-typed as a requests Response
    def get(self, *args, **kwargs):
        url = args[0]
        if 'params' in kwargs:
            params = kwargs['params'].items()
            params = dict(filter(lambda kv: kv[1] is not None, params))
            url = "%s?%s" % (url, urlencode(params))
        return self.tc.get(url)

    def post(self, *args, **kwargs):
        url = args[0]
        return self.tc.post(url, **kwargs)

tcw = TestClientWrapper(app.test_client())


class TestBookService(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        cls.tcw = TestClientWrapper(app.test_client())
        APP_CONFIG.db_file = lambda: DB_FILE
        cls.db = Database(APP_CONFIG.db_file())
        schema_path = os.path.join(os.path.dirname(__file__), 'books.schema')
        with open(schema_path, 'r') as file:
            cls.schema = file.read()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def setUp(self):
        self.db.con.cursor().executescript(self.schema)
        self.bs = WebBookService()

    def tearDown(self):
        self.db.con.cursor().execute('DROP TABLE Books')
        self.db.con.cursor().execute('DROP TABLE Users')
        self.db.con.cursor().execute('DROP TABLE ActionLogs')

    @mock.patch('requests.get', side_effect=tcw.get)
    def test_getBook_exists(self, _):
        self.db.putBook('1234', 'A Book', 'Somebody', 'cat', 'year', 'img')

        res = self.bs.getBook(1234)

        self.assertEqual(res.title, 'A Book')
        self.assertEqual(res.author, 'Somebody')

    @mock.patch('requests.get', side_effect=tcw.get)
    def test_getBook_doesNotExist(self, _):
        with self.assertRaises(NotFoundException):
            self.bs.getBook(1234)

    @mock.patch('requests.get', side_effect=tcw.get)
    def test_listBooks_noQuery(self, _):
        self.db.putBook('1234', 'A Book', 'Somebody', 'cat', 'year', 'img')
        self.db.putBook('5678', 'Sequel', 'Somebody', 'cat', 'year', 'img')

        res = self.bs.listBooks()

        self.assertEqual(len(res), 2)

    @mock.patch('requests.get', side_effect=tcw.get)
    def test_listBooks_query(self, _):
        self.db.putBook('1234', 'A Book', 'Somebody', 'cat', 'year', 'img')
        self.db.putBook('5678', 'Sequel', 'Somebody', 'cat', 'year', 'img')

        res = self.bs.listBooks('sequel')

        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].title, 'Sequel')

    @mock.patch('requests.get', side_effect=tcw.get)
    def test_listBooksByStatus_checkedOut(self, _):
        self.db.putUser(1234, 'somebody', 'email')
        self.db.putBook('isbn-in', 'Book 1', 'Author', 'cat', 'year', 'img')
        self.db.putBook('isbn-out', 'Book 2', 'Author', 'cat', 'year', 'img')
        self.db.putLog('isbn-in', Action.CREATE)
        self.db.putLog('isbn-out', Action.CHECKOUT, 1234)

        res = self.bs.listBooksByStatus(True)

        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].isbn, 'isbn-out')

    @mock.patch('requests.get', side_effect=tcw.get)
    def test_listBooksByStatus_checkedIn(self, _):
        self.db.putUser(1234, 'somebody', 'email')
        self.db.putBook('isbn-in', 'Book 1', 'Author', 'cat', 'year', 'img')
        self.db.putBook('isbn-out', 'Book 2', 'Author', 'cat', 'year', 'img')
        self.db.putLog('isbn-in', Action.CREATE)
        self.db.putLog('isbn-out', Action.CHECKOUT, 1234)

        res = self.bs.listBooksByStatus(False)

        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].isbn, 'isbn-in')

    @mock.patch('requests.get', side_effect=tcw.get)
    @mock.patch('requests.post', side_effect=tcw.post)
    def test_createBook(self, *_):
        book = Book('1234', 'A Book', 'Somebody', 'cat', 'year', 'img')

        self.bs.createBook(book)
        res = self.bs.getBook('1234')

        self.assertEqual(res, book)

    @mock.patch('requests.get', side_effect=tcw.get)
    @mock.patch('requests.post', side_effect=tcw.post)
    def test_checkoutBook(self, *_):
        self.db.putBook('isbn1', '', '', '', '', '')
        user = User(1234, 'user', 'fake-email')
        self.db.putUser(user.user_id, user.name, user.email)

        self.bs.checkoutBook('isbn1', user)
        res = self.bs.getBook('isbn1')

        self.assertEqual(res.is_out, True)
        self.assertEqual(res.checkout_user, 'user')
        self.assertAboutNow(res.checkout_time)

    @mock.patch('requests.post', side_effect=tcw.post)
    def test_checkoutBook_alreadyOut(self, _):
        self.db.putBook('isbn1', '', '', '', '', '')
        user = User(1234, 'user', 'fake-email')
        self.db.putUser(user.user_id, user.name, user.email)
        self.bs.checkoutBook('isbn1', user)

        with self.assertRaises(InvalidStateException):
            self.bs.checkoutBook('isbn1', user)

    @mock.patch('requests.get', side_effect=tcw.get)
    @mock.patch('requests.post', side_effect=tcw.post)
    def test_returnBook(self, *_):
        self.db.putBook('isbn1', '', '', '', '', '')
        user = User(1234, 'user', 'fake-email')
        self.db.putUser(user.user_id, user.name, user.email)
        self.bs.checkoutBook('isbn1', user)
        time.sleep(1)

        self.bs.returnBook('isbn1')
        res = self.bs.getBook('isbn1')
        log = self.db.getLatestLog('isbn1')

        self.assertEqual(res.is_out, False)
        self.assertEqual(res.checkout_user, '')
        self.assertEqual(res.checkout_time, '')
        self.assertAboutNow(log[1])
        self.assertEqual(log[2], Action.RETURN.value)
        self.assertEqual(log[3], 1234)

    @mock.patch('requests.post', side_effect=tcw.post)
    def test_returnBook_notOut(self, _):
        self.db.putBook('isbn1', '', '', '', '', '')

        with self.assertRaises(InvalidStateException):
            self.bs.returnBook('isbn1')


if __name__ == '__main__':
    unittest.main()
