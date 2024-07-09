import os
import sys

ERROR_STYLE = 'Error.TLabel'
TITLE_STYLE = 'Title.TLabel'
AUTHOR_STYLE = 'Author.TLabel'
METADATA_STYLE = 'Metadata.TLabel'
HEADER_STYLE = 'Header.TLabel'

# All user IDs are 6 digits (except mine, which is 1)
MIN_USER_ID = 100000
MAX_USER_ID = 999999

POPUP_WINDOW_SIZE = '480x320'

# A bit inappropriate to be doing method calls in a file called "constants"...
# But this is where it makes the most sense for this to be. Oh well
ROOT_PATH = os.path.dirname(__file__)
DB_FILE = os.path.join(ROOT_PATH, 'backend', 'books.db')
MAILGUN_APIKEY_FILE = os.path.join(ROOT_PATH, 'notifs', 'mailgun.secret')

# Override some values when packaged into an executable
if getattr(sys, 'frozen', False):
    # Works because this is a one-file executable. If one-directory instead,
    # this would need to use sys._MEIPASS instead of sys.executable
    # See: https://stackoverflow.com/questions/404744
    ROOT_PATH = os.path.dirname(sys.executable)
    # lives alongside the executable
    DB_FILE = os.path.join(ROOT_PATH, 'books.db')
    # disable notifications
    MAILGUN_APIKEY_FILE = ''
