import unittest
from datetime import datetime, UTC
import time

from backend.db import Action, Database
from backend.testbase import BaseTestCase

class TestDatabase(BaseTestCase):

    TEST_DATABASE = ':memory:'

    def setUp(self):
        self.db = Database(self.TEST_DATABASE)
        with open('books.schema', 'r') as file:
            schema = file.read()
            self.db.con.cursor().executescript(schema)

    def tearDown(self):
        self.db.close()

    def test_check_tablesExist(self):
        with self.assertNoLogs('db_logger', level='WARNING') as lc:
            self.db.check()

    def test_check_tablesMissing(self):
        self.db.con.cursor().execute('DROP TABLE Books')
        self.db.con.cursor().execute('DROP TABLE ActionLogs')
        with self.assertLogs('db_logger', level='WARNING') as lc:
            self.db.check()
            self.assertEqual(lc.output,
                             ['WARNING:db_logger:Table Books does not exist',
                              'WARNING:db_logger:Table ActionLogs does not exist'])

    def test_putAndGet(self):
        self.db.putBook('some-isbn', 'Really Cool Book', 'Smart Person', 'Non-fiction', '1998', 'url')
        res = self.db.getBook('some-isbn')

        self.assertEqual(res, ('some-isbn', 'Really Cool Book', 'Smart Person', 'Non-fiction', '1998', 'url'))

    def test_list(self):
        self.db.putBook('isbn1', 'Babel', 'R.F. Kuang', 'Fiction', '2022', 'url')
        self.db.putBook('isbn2', 'Looking for Alaska', 'John Green', 'Fiction', '2005', 'url')

        res = self.db.listBooks()

        self.assertEqual(res,
                         [('isbn1', 'Babel', 'R.F. Kuang', 'Fiction', '2022', 'url'),
                          ('isbn2', 'Looking for Alaska', 'John Green', 'Fiction', '2005', 'url')])

    def test_logs_putAndGet(self):
        self.db.putLog('some-isbn', Action.CREATE, 'brian')

        res = self.db.getLatestLog('some-isbn')

        self.assertEqual(res[0], 'some-isbn')
        self.assertEqual(res[2], Action.CREATE.value)
        self.assertEqual(res[3], 'brian')
        self.assertAboutNow(res[1])

    def test_logs_getsMostRecent(self):
        self.db.putLog('some-isbn', Action.CREATE, 'brian')
        time.sleep(1)  # Hack to keep the timestamps from colliding
        self.db.putLog('some-isbn', Action.CHECKOUT, 'friend')

        res = self.db.getLatestLog('some-isbn')

        self.assertEqual(res[0], 'some-isbn')
        self.assertEqual(res[2], Action.CHECKOUT.value)
        self.assertEqual(res[3], 'friend')

    def test_logs_getsMatchingIsbn(self):
        self.db.putLog('isbn1', Action.CREATE, 'brian')
        self.db.putLog('isbn2', Action.CHECKOUT, 'friend')

        res = self.db.getLatestLog('isbn1')

        self.assertEqual(res[0], 'isbn1')
        self.assertEqual(res[2], Action.CREATE.value)
        self.assertEqual(res[3], 'brian')

    def test_logs_noneMatching(self):
        res = self.db.getLatestLog('isbn1')

        self.assertEqual(res, ('isbn1', '', 0, ''))


if __name__ == '__main__':
    unittest.main()
