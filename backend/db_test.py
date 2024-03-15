import unittest
from db import Database

class TestDatabase(unittest.TestCase):

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
        self.db.con.cursor().execute('DROP TABLE CheckoutLogs')
        with self.assertLogs('db_logger', level='WARNING') as lc:
            self.db.check()
            self.assertEqual(lc.output,
                             ['WARNING:db_logger:Table Books does not exist',
                              'WARNING:db_logger:Table CheckoutLogs does not exist'])

    def test_putAndGet(self):
        self.db.put('some-isbn', 'Really Cool Book')
        res = self.db.get('some-isbn')

        self.assertEqual(res, ('some-isbn', 'Really Cool Book'))

    def test_list(self):
        self.db.put('isbn1', 'Babel')
        self.db.put('isbn2', 'Looking for Alaska')

        res = self.db.list()

        self.assertEqual(res, [('isbn1', 'Babel'), ('isbn2', 'Looking for Alaska')])


if __name__ == '__main__':
    unittest.main()
