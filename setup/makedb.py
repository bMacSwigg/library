import sqlite3
import sys

if len(sys.argv) < 3:
    print("Not enough arguments provided")
    sys.exit(1)

schema_path = sys.argv[1]
db_path = sys.argv[2]

with open(schema_path, 'r') as schema:
    con = sqlite3.connect(db_path)
    con.cursor().executescript(schema.read())
    con.close()
