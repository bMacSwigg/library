import unittest
from db import Database

class TestDatabase(unittest.TestCase):

    TEST_DATABASE = ':memory:'

    def setUp(self):
        self.db = Database(self.TEST_DATABASE)

    def tearDown(self):
        self.db.close()

    def test_initTables_tableAlreadyExists(self):
        self.db.initTables()

        self.db.initTables()  # Second call does not raise an error

    def test_putAndGet(self):
        self.db.initTables()

        self.db.put('some-isbn', 'Really Cool Book')
        res = self.db.get('some-isbn')

        self.assertEqual(res, ('some-isbn', 'Really Cool Book'))

    def test_list(self):
        self.db.initTables()
        self.db.put('isbn1', 'Babel')
        self.db.put('isbn2', 'Looking for Alaska')

        res = self.db.list()

        self.assertEqual(res, [('isbn1', 'Babel'), ('isbn2', 'Looking for Alaska')])


if __name__ == '__main__':
    unittest.main()
