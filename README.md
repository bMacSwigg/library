# library
Personal library catalog

## Setup

Add this project's parent directory to the PYTHONPATH, to ensure imports work.

Install dependencies:
*  Pillow, which is needed for displaying images
*  mailgun, which is needed for sending emails
*  sendgrid, which could be used for sending emails, if it was a good product

```
pip install -r requirements.txt
```

To create a DB based off the schema (if one doesn't already exist), use the
SQLite CLI to run:

```
sqlite3 books.db < books.schema
```

If the DB already exists, and you need to edit it, you will need to do so
manually (e.g. via `ALTER TABLE` commands).

## Useful commands

Joining logs table with books & users to get human-readable titles & names

```sql
SELECT
  B.Title AS Title,
  L.Timestamp AS Time,
  L.Action AS Action,
  U.Name AS Name
FROM
  ActionLogs AS L
  LEFT JOIN Books AS B ON L.Isbn = B.Isbn
  LEFT JOIN Users AS U ON L.UserId = U.Id;
```