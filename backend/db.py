import sqlite3

class Database:

    BOOKS_TABLENAME = 'Books'

    def __init__(self, filename):
        self.filename = filename
        self.con = sqlite3.connect(filename)

    def __del__(self):
        self.close()

    def close(self):
        self.con.close()

    def initTables(self):
        """Checks if the necessary tables exist, and if not, creates them."""
        cur = self.con.cursor()
        booksQuery = ('SELECT name FROM sqlite_master WHERE name="%s"' %
                      self.BOOKS_TABLENAME)
        if cur.execute(booksQuery).fetchone() is None:
            cur.execute('CREATE TABLE %s(Isbn, Title)' % self.BOOKS_TABLENAME)
        else:
            print('Table %s already exists' % self.BOOKS_TABLENAME)

    def get(self, isbn):
        cur = self.con.cursor()
        query = ('SELECT * FROM %s WHERE Isbn="%s"' %
                 (self.BOOKS_TABLENAME, isbn))
        return cur.execute(query).fetchone()

    def put(self, isbn, title):
        cur = self.con.cursor()
        query = ('INSERT INTO %s VALUES ("%s", "%s")' %
                 (self.BOOKS_TABLENAME, isbn, title))
        cur.execute(query)
        self.con.commit()

    def list(self):
        cur = self.con.cursor()
        query = 'SELECT * FROM %s' % self.BOOKS_TABLENAME
        return cur.execute(query).fetchall()
