from tkinter import *
from tkinter import ttk

from backend.api import BookService, NotFoundException
from constants import *
from ui.book_list import BookList
from ui.image_loader import CachedImageLoader
from ui.scrollable import ScrollFrame
from ui.tabs.base import BaseTab

class CirculationTab(BaseTab):
    """Tab for scanning in/out books and seeing what is currently lent out"""

    def __init__(self, tab: ttk.Frame, bs: BookService, cil: CachedImageLoader):
        super().__init__(tab, bs)
        self.cil = cil

    def _lookupBook(self):
        isbn = self.isbn.get()
        if not isbn:
            self._showError('Missing ISBN')
            return
        else:
            self._clearError()
        self.refresh()
        try:
            book = self.bs.getBook(isbn)
            BookList(self.bookframe, [book], self.bs, self.cil).display(False)
        except NotFoundException:
            self._showError('No book with ISBN %s' % isbn)

    def _checkedOutBooks(self):
        self.refresh()
        books = self.bs.listBooksByStatus(True)
        BookList(self.bookframe, books, self.bs, self.cil).display(False)

    def _clearError(self):
        if hasattr(self, 'error') and self.error.winfo_exists():
            self.error.destroy()

    def _showError(self, msg: str):
        self._clearError()
        self.error = ttk.Label(self.lookupframe, text=('Error: %s' % msg))
        self.error.configure(style=ERROR_STYLE)
        self.error.grid(column=4, row=0)

    def _make(self):
        self.lookupframe = ttk.Frame(self.tab)
        self.lookupframe.pack(side='top', fill='x', expand=False)

        self.isbn = StringVar()
        isbnLabel = ttk.Label(self.lookupframe, text='ISBN:')
        isbnLabel.grid(column=0, row=0)
        isbnEntry = ttk.Entry(self.lookupframe, width=20, textvariable=self.isbn)
        isbnEntry.grid(column=1, row=0)
        isbnEntry.bind('<Return>', lambda e: self._lookupBook())
        isbnEntry.focus()
        lookup = ttk.Button(self.lookupframe, text='Lookup',
                            command=self._lookupBook)
        lookup.grid(column=2, row=0)
        checkedOut = ttk.Button(self.lookupframe, text='Checked Out',
                                command=self._checkedOutBooks)
        checkedOut.grid(column=3, row=0)

        scrollframe = ScrollFrame(self.tab)
        scrollframe.pack(side='bottom', fill='both', expand=True)
        self.bookframe = scrollframe.viewPort
