# library
Personal library catalog

## Setup

Add this project directory to the PYTHONPATH, to ensure imports work

To create a DB based off the schema (if one doesn't already exist), run:

```
sqlite3 books.db < books.schema
```

If the DB already exists, and you need to edit it, you will need to do so
manually (e.g. via `ALTER TABLE` commands).