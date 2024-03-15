import unittest
from backend.api import BookService
from backend.db import Database
from backend.models import Book

class TestBookService(unittest.TestCase):

    TEST_DATABASE = ':memory:'

    def setUp(self):
        self.books = BookService()
        self.books.db = Database(self.TEST_DATABASE)
        with open('books.schema', 'r') as file:
            schema = file.read()
            self.books.db.con.cursor().executescript(schema)

    def test_getBook_exists(self):
        self.books.db.put('isbn1', 'title', 'author')

        book = self.books.getBook('isbn1')

        self.assertEqual(book, Book('isbn1', 'title', 'author'))

    def test_getBook_doesNotExist(self):
        with self.assertRaises(TypeError):
            # Not ideal error handling, but at least it's tested? lol
            self.books.getBook('isbn1')

    def test_listBooks(self):
        self.books.db.put('isbn1', 'Babel', 'R.F. Kuang')
        self.books.db.put('isbn2', 'Looking For Alaska', 'John Green')

        books = self.books.listBooks()

        self.assertEqual(books,
                         [Book('isbn1', 'Babel', 'R.F. Kuang'),
                          Book('isbn2', 'Looking For Alaska', 'John Green')])


if __name__ == '__main__':
    unittest.main()
