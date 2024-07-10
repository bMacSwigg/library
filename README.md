# library
Personal library catalog

## Development

### Setup

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

### Useful commands

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

## Installing as executable

### Windows

NOTE: You need to already have Python3 installed for this to work

First, [add an exclusion](https://support.microsoft.com/en-us/windows/add-an-exclusion-to-windows-security-811816c0-4dfd-af4a-47e4-c301afe13b26#:~:text=Go%20to%20Start%20%3E%20Settings%20%3E%20Update,%2C%20file%20types%2C%20or%20process) for the GitHub directory, so Windows won't think the executable is a virus.

NOTE: This is necessary because the compiled executable isn't signed by any developer certificate, and Windows hates that.

Next, run the install script `setup\win\install.bat`. This will install the necessary dependencies, and bundle the code from the source files into an executable.

The script will also give you the option of setting up a new blank database. The first time you run it, you will need to do this. If you use this script to update your installation in the future, you will want to say "No"; otherwise your existing database will be wiped.

The .exe will now live in the `run` subdirectory. You probably can't move it out of the GitHub repo without Windows deciding it's a virus and nuking it. However, you can create a desktop shortcut to it for convenience.
