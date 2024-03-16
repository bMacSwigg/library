import logging
import sqlite3

class Database:

    BOOKS_TABLENAME = 'Books'
    LOGS_TABLENAME = 'CheckoutLogs'

    def __init__(self, filename):
        self.filename = filename
        self.con = sqlite3.connect(filename)
        self.logger = logging.getLogger('db_logger')
        logging.basicConfig(level=logging.WARNING)

    def __del__(self):
        self.close()

    def close(self):
        self.con.close()

    def check(self):
        """Checks if the necessary tables exist."""
        cur = self.con.cursor()
        tables = cur.execute('SELECT name FROM sqlite_schema').fetchall()
        self._findTable(self.BOOKS_TABLENAME, tables)
        self._findTable(self.LOGS_TABLENAME, tables)

    def _findTable(self, tablename, tables):
        if (tablename,) not in tables:
            self.logger.warning('Table %s does not exist' % tablename)

    def get(self, isbn):
        cur = self.con.cursor()
        query = ('SELECT * FROM %s WHERE Isbn="%s"' %
                 (self.BOOKS_TABLENAME, isbn))
        return cur.execute(query).fetchone()

    def put(self, isbn, title, author, cat, year, img):
        cur = self.con.cursor()
        query = ('INSERT INTO %s VALUES ("%s", "%s", "%s", "%s", "%s", "%s")' %
                 (self.BOOKS_TABLENAME, isbn, title, author, cat, year, img))
        cur.execute(query)
        self.con.commit()

    def list(self):
        cur = self.con.cursor()
        query = 'SELECT * FROM %s' % self.BOOKS_TABLENAME
        return cur.execute(query).fetchall()
