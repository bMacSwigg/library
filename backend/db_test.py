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
        self.db.con.cursor().execute('DROP TABLE Users')
        with self.assertLogs('db_logger', level='WARNING') as lc:
            self.db.check()
            self.assertEqual(lc.output,
                             ['WARNING:db_logger:Table Books does not exist',
                              'WARNING:db_logger:Table ActionLogs does not exist',
                              'WARNING:db_logger:Table Users does not exist'])

    def test_book_putAndGet(self):
        self.db.putBook('some-isbn', 'Really Cool Book', 'Smart Person', 'Non-fiction', '1998', 'url')
        res = self.db.getBook('some-isbn')

        self.assertEqual(res, ('some-isbn', 'Really Cool Book', 'Smart Person', 'Non-fiction', '1998', 'url'))

    def test_book_list(self):
        self.db.putBook('isbn1', 'Babel', 'R.F. Kuang', 'Fiction', '2022', 'url')
        self.db.putBook('isbn2', 'Looking for Alaska', 'John Green', 'Fiction', '2005', 'url')

        res = self.db.listBooks()

        self.assertEqual(res,
                         [('isbn1', 'Babel', 'R.F. Kuang', 'Fiction', '2022', 'url'),
                          ('isbn2', 'Looking for Alaska', 'John Green', 'Fiction', '2005', 'url')])

    def test_book_listWithSearch(self):
        self.db.putBook('isbn1', 'Babel', 'R.F. Kuang', 'Fiction', '2022', 'url')
        self.db.putBook('isbn2', 'Looking for Alaska', 'John Green', 'Fiction', '2005', 'url')

        self.assertEqual(self.db.listBooks('for'),
                         [('isbn2', 'Looking for Alaska', 'John Green', 'Fiction', '2005', 'url')])
        self.assertEqual(self.db.listBooks('Kuang'),
                         [('isbn1', 'Babel', 'R.F. Kuang', 'Fiction', '2022', 'url')])
        self.assertEqual(self.db.listBooks('a'),
                         [('isbn1', 'Babel', 'R.F. Kuang', 'Fiction', '2022', 'url'),
                          ('isbn2', 'Looking for Alaska', 'John Green', 'Fiction', '2005', 'url')])

    def test_logs_putAndGet(self):
        self.db.putLog('some-isbn', Action.CREATE, 1234)

        res = self.db.getLatestLog('some-isbn')

        self.assertEqual(res[0], 'some-isbn')
        self.assertEqual(res[2], Action.CREATE.value)
        self.assertEqual(res[4], 1234)
        self.assertAboutNow(res[1])

    def test_logs_getsMostRecent(self):
        self.db.putLog('some-isbn', Action.CREATE, 1234)
        time.sleep(1)  # Hack to keep the timestamps from colliding
        self.db.putLog('some-isbn', Action.CHECKOUT, 5678)

        res = self.db.getLatestLog('some-isbn')

        self.assertEqual(res[0], 'some-isbn')
        self.assertEqual(res[2], Action.CHECKOUT.value)
        self.assertEqual(res[4], 5678)

    def test_logs_getsMatchingIsbn(self):
        self.db.putLog('isbn1', Action.CREATE, 1234)
        self.db.putLog('isbn2', Action.CHECKOUT, 5678)

        res = self.db.getLatestLog('isbn1')

        self.assertEqual(res[0], 'isbn1')
        self.assertEqual(res[2], Action.CREATE.value)
        self.assertEqual(res[4], 1234)

    def test_logs_noneMatching(self):
        res = self.db.getLatestLog('isbn1')

        self.assertEqual(res, ('isbn1', '', 0, '', 0))

    def test_logs_list(self):
        self.db.putLog('isbn1', Action.CREATE, 1234)
        time.sleep(1)  # Hack to keep the timestamps from colliding
        self.db.putLog('isbn1', Action.CHECKOUT, 5678)
        self.db.putLog('isbn2', Action.CREATE, 9001)

        res = self.db.listLogs('isbn1')

        self.assertEqual(len(res), 2)
        self.assertEqual(res[0][0], 'isbn1')
        self.assertEqual(res[0][2], Action.CREATE.value)
        self.assertEqual(res[0][4], 1234)
        self.assertEqual(res[1][0], 'isbn1')
        self.assertEqual(res[1][2], Action.CHECKOUT.value)
        self.assertEqual(res[1][4], 5678)

    def test_user_putAndGet(self):
        self.db.putUser(1234, 'John Doe', 'john@example.com')
        res = self.db.getUser(1234)

        self.assertEqual(res, (1234, 'John Doe', 'john@example.com'))

    def test_user_list(self):
        self.db.putUser(1234, 'John Doe', 'john@example.com')
        self.db.putUser(5678, 'Jane Doe', 'jane@example.com')

        res = self.db.listUsers()

        self.assertEqual(res,
                         [(1234, 'John Doe', 'john@example.com'),
                          (5678, 'Jane Doe', 'jane@example.com')])



if __name__ == '__main__':
    unittest.main()
