import os
import sys
import unittest

from library.config import AppConfig


class TestConfig(unittest.TestCase):

    def setUp(self):
        # so it can find the config for prod versions
        sys._MEIPASS = os.getcwd()

    def test_owner_dev(self):
        ac = AppConfig()
        self.assertEqual(ac.owner(), 'Brian')

    def test_owner_prod(self):
        ac = AppConfig(override_prod=True)
        self.assertEqual(ac.owner(), 'Brian')

    def test_dbfile_dev(self):
        ac = AppConfig()
        expected_subpath = os.path.normpath('library/src/library/backend/books.db')
        self.assertIn(expected_subpath, ac.db_file())

    def test_dbfile_prod(self):
        ac = AppConfig(override_prod=True)
        # sys.executable root path will be the Python exe
        self.assertIn('books.db', ac.db_file())
        self.assertNotIn('backend', ac.db_file())

    def test_mailgunkey_dev(self):
        ac = AppConfig()
        expected_subpath = os.path.normpath('library/src/library/notifs/mailgun.secret')
        self.assertIn(expected_subpath, ac.mailgun_apikey_file())

    def test_mailgunkey_prod(self):
        ac = AppConfig(override_prod=True)
        self.assertIsNone(ac.mailgun_apikey_file())

    def test_iconfile_dev(self):
        ac = AppConfig()
        expected_subpath = os.path.normpath('library/src/library/book-solid.ico')
        self.assertIn(expected_subpath, ac.icon_file())

    def test_iconfile_prod(self):
        ac = AppConfig(override_prod=True)
        expected_subpath = os.path.normpath('library/src/library/book-solid.ico')
        self.assertIn(expected_subpath, ac.icon_file())

    def test_logfile_dev(self):
        ac = AppConfig()
        expected_subpath = os.path.normpath('library/src/library/library.log')
        self.assertIn(expected_subpath, ac.log_file())

    def test_logfile_prod(self):
        ac = AppConfig(override_prod=True)
        self.assertIn('library.log', ac.log_file())


if __name__ == '__main__':
    unittest.main()
