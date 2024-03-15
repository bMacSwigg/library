# TODO: give this a better class structure

from tkinter import *
from tkinter import ttk

from backend.api import BookService
from backend.models import Book

ERROR_STYLE = 'Error.TLabel'
TITLE_STYLE = 'Title.TLabel'

class _BaseTab:

    def __init__(self, tab, bs):
        self.tab = tab
        self.bs = bs

    def _make(self):
        pass

    def refresh(self):
        for child in self.tab.winfo_children():
            child.destroy()
        self._make()

class CatalogTab(_BaseTab):

    def _getBooks(self) -> list[Book]:
        return self.bs.listBooks()

    def _makeBookRow(self, book: Book, ind: int):
        row = ttk.Frame(self.tab)
        row.grid(column=0, row=ind, sticky=(W, E))
        title = ttk.Label(row, text=book.title)
        title.grid(column=1, row=0, columnspan=2, sticky=W)
        title.configure(style=TITLE_STYLE)
        ttk.Label(row, text=book.author).grid(column=1, row=1, sticky=W)
        ttk.Label(row, text=('ISBN: %s' % book.isbn)).grid(column=2, row=1, sticky=E)

    def _make(self):
        books = self._getBooks()
        for i,book in enumerate(books):
            self._makeBookRow(book, i)

class ImportTab(_BaseTab):

    def _lookupBook(self, isbn):
        print('TODO: lookup %s' % isbn.get())

    def _createBook(self, isbn, title, author):
        i = isbn.get()
        t = title.get()
        a = author.get()
        if i and t and a:
            book = Book(i, t, a)
            self.bs.createBook(book)
            self.refresh()
        else:
            self._showError('Missing properties')

    def _showError(self, msg):
        if hasattr(self, 'error') and self.error.winfo_exists():
            self.error.destroy()
        self.error = ttk.Label(self.tab, text=('Error: %s' % msg))
        self.error.configure(style=ERROR_STYLE)
        self.error.grid(column=0, row=4, columnspan=2)

    def _make(self):
        isbn = StringVar()
        isbnLabel = ttk.Label(self.tab, text="ISBN:")
        isbnLabel.grid(column=0, row=0)
        isbnEntry = ttk.Entry(self.tab, width=20, textvariable=isbn)
        isbnEntry.grid(column=1, row=0)
        isbnEntry.bind('<Return>', lambda e: self._lookupBook(isbn))

        lookup = ttk.Button(self.tab, text="Lookup",
                            command=lambda: self._lookupBook(isbn))
        lookup.grid(column=2, row=0)

        title = StringVar()
        titleLabel = ttk.Label(self.tab, text="Title:")
        titleLabel.grid(column=0, row=1)
        titleEntry = ttk.Entry(self.tab, width=20, textvariable=title)
        titleEntry.grid(column=1, row=1)

        author = StringVar()
        authorLabel = ttk.Label(self.tab, text="Author:")
        authorLabel.grid(column=0, row=2)
        authorEntry = ttk.Entry(self.tab, width=20, textvariable=author)
        authorEntry.grid(column=1, row=2)

        create = ttk.Button(self.tab, text="Create",
                            command=lambda: self._createBook(isbn, title, author))
        create.grid(column=0, row=3, columnspan=2)
    
class AppWindow:

    def __init__(self):
        self.bs = BookService()

    def refreshAllTabs(self, event):
        # TODO: Would be better to just figure out which tab was picked
        self.catalogTab.refresh()
        self.importTab.refresh()

    def main(self):
        root = Tk()
        root.title('Brian\'s Library')
        root.geometry('600x400')

        ttk.Style().configure(ERROR_STYLE, foreground='red')
        ttk.Style().configure(TITLE_STYLE, font=('Arial', 14, 'bold'))

        mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        tabs = ttk.Notebook(mainframe)
        tabCatalog = ttk.Frame(tabs)
        tabCheckout = ttk.Frame(tabs)
        tabImport = ttk.Frame(tabs)
        tabs.add(tabCatalog, text='Catalog')
        tabs.add(tabCheckout, text='Checkout')
        tabs.add(tabImport, text='Import')
        tabs.pack(expand=1, fill='both')
        tabs.bind('<<NotebookTabChanged>>', self.refreshAllTabs)

        self.catalogTab = CatalogTab(tabCatalog, self.bs)
        self.catalogTab.refresh()
        self.importTab = ImportTab(tabImport, self.bs)
        self.importTab.refresh()

        root.mainloop()
