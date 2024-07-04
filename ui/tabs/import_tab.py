from tkinter import *
from tkinter import ttk

from backend.api import BookService, LookupService
from backend.models import Book
from constants import *
from ui.tabs.base import BaseTab


class ImportTab(BaseTab):
    """Tab for adding new books to the library"""

    def __init__(self, tab: ttk.Frame, bs: BookService, ls: LookupService):
        super().__init__(tab, bs)
        self.ls = ls

    def _lookupBook(self):
        isbn = self.isbn.get()
        if not isbn:
            self._showError('Missing ISBN')
            return
        else:
            self._clearError()
        book = self.ls.lookupIsbn(isbn)
        self.title.set(book.title)
        self.author.set(book.author)
        self.category.set(book.category)
        self.year.set(book.year)
        self.thumbnail.set(book.thumbnail)

    def _createBook(self):
        i = self.isbn.get()
        t = self.title.get()
        a = self.author.get()
        c = self.category.get()
        y = self.year.get()
        url = self.thumbnail.get()
        # It's okay for the URL to be empty
        if all([i, t, a, c, y]):
            book = Book(i, t, a, c, y, url)
            self.bs.createBook(book)
            self.refresh()
        else:
            self._showError('Missing properties')

    def _clearError(self):
        if hasattr(self, 'error') and self.error.winfo_exists():
            self.error.destroy()

    def _showError(self, msg):
        self._clearError()
        self.error = ttk.Label(self.tab, text=('Error: %s' % msg))
        self.error.configure(style=ERROR_STYLE)
        self.error.grid(column=0, row=7, columnspan=2)

    def _make(self):
        self.isbn = StringVar()
        isbnLabel = ttk.Label(self.tab, text="ISBN:")
        isbnLabel.grid(column=0, row=0)
        isbnEntry = ttk.Entry(self.tab, width=20, textvariable=self.isbn)
        isbnEntry.grid(column=1, row=0)
        isbnEntry.bind('<Return>', lambda e: self._lookupBook())
        isbnEntry.focus()

        lookup = ttk.Button(self.tab, text="Lookup",
                            command=self._lookupBook)
        lookup.grid(column=2, row=0)

        self.title = StringVar()
        titleLabel = ttk.Label(self.tab, text="Title:")
        titleLabel.grid(column=0, row=1)
        titleEntry = ttk.Entry(self.tab, width=20, textvariable=self.title)
        titleEntry.grid(column=1, row=1)

        self.author = StringVar()
        authorLabel = ttk.Label(self.tab, text="Author:")
        authorLabel.grid(column=0, row=2)
        authorEntry = ttk.Entry(self.tab, width=20, textvariable=self.author)
        authorEntry.grid(column=1, row=2)

        self.category = StringVar()
        categoryLabel = ttk.Label(self.tab, text="Category:")
        categoryLabel.grid(column=0, row=3)
        categoryEntry = ttk.Entry(self.tab, width=20, textvariable=self.category)
        categoryEntry.grid(column=1, row=3)

        self.year = StringVar()
        yearLabel = ttk.Label(self.tab, text="Publication Year:")
        yearLabel.grid(column=0, row=4)
        yearEntry = ttk.Entry(self.tab, width=20, textvariable=self.year)
        yearEntry.grid(column=1, row=4)

        self.thumbnail = StringVar()
        thumbnailLabel = ttk.Label(self.tab, text="Thumbnail:")
        thumbnailLabel.grid(column=0, row=5)
        thumbnailEntry = ttk.Entry(self.tab, width=20, textvariable=self.thumbnail)
        thumbnailEntry.grid(column=1, row=5)

        create = ttk.Button(self.tab, text="Create", command=self._createBook)
        create.grid(column=0, row=6, columnspan=2)
