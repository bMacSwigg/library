from enum import Enum
import logging
import sqlite3

class Action(Enum):
    UNKNOWN = 0
    CREATE = 1
    CHECKOUT = 2
    RETURN = 3

class Database:

    BOOKS_TABLENAME = 'Books'
    LOGS_TABLENAME = 'ActionLogs'

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

    def getBook(self, isbn):
        cur = self.con.cursor()
        query = ('SELECT * FROM %s WHERE Isbn="%s"' %
                 (self.BOOKS_TABLENAME, isbn))
        return cur.execute(query).fetchone()

    def putBook(self, isbn, title, author, cat, year, img):
        cur = self.con.cursor()
        query = ('INSERT INTO %s VALUES ("%s", "%s", "%s", "%s", "%s", "%s")' %
                 (self.BOOKS_TABLENAME, isbn, title, author, cat, year, img))
        cur.execute(query)
        self.con.commit()

    def listBooks(self):
        cur = self.con.cursor()
        query = 'SELECT * FROM %s' % self.BOOKS_TABLENAME
        return cur.execute(query).fetchall()

    def putLog(self, isbn: str, action: Action, user: str):
        cur = self.con.cursor()
        query = ('INSERT INTO %s VALUES ("%s", datetime("now"), %s, "%s")' %
                 (self.LOGS_TABLENAME, isbn, action.value, user))
        cur.execute(query)
        self.con.commit()

    def getLatestLog(self, isbn: str):
        cur = self.con.cursor()
        query = ('SELECT * FROM %s WHERE Isbn="%s" ORDER BY Timestamp DESC LIMIT 1' %
                 (self.LOGS_TABLENAME, isbn))
        return cur.execute(query).fetchone() or (isbn, '', Action.UNKNOWN.value, '')
