import sqlite3

class Database:

    BOOKS_TABLENAME = 'Books'

    def __init__(self, filename):
        self.filename = filename
        self.con = sqlite3.connect(filename)

    def __del__(self):
        self.con.close()

    def initializeBooksTables(self):
        cur = self.con.cursor()
        cur.execute('CREATE TABLE %s(Isbn, Title)' % self.BOOKS_TABLENAME)

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
