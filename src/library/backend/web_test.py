from flask.testing import FlaskClient
import json
from threading import Thread
import os
import time
import unittest
from unittest import mock
from urllib.parse import urlencode
from werkzeug.test import TestResponse

from library.backend.api import NotFoundException
from library.backend.db import Database
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


if __name__ == '__main__':
    unittest.main()