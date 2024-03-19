import unittest
from backend.db import Database

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


if __name__ == '__main__':
    unittest.main()
