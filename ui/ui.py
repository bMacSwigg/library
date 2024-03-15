# TODO: give this a better class structure

from tkinter import *
from tkinter import ttk

from backend.api import BookService
from backend.models import Book

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
        ttk.Label(row, text=('Title: %s' % book.title)).grid(column=0, row=0, sticky=W)
        ttk.Label(row, text=('ISBN: %s' % book.isbn)).grid(column=1, row=0, sticky=E)

    def _make(self):
        books = self._getBooks()
        for i,book in enumerate(books):
            self._makeBookRow(book, i)

class ImportTab(_BaseTab):

    def _createBook(self, isbn, title, author):
        book = Book(isbn.get(), title.get(), author.get())
        self.bs.createBook(book)

    def _make(self):
        isbn = StringVar()
        isbnLabel = ttk.Label(self.tab, text="ISBN:")
        isbnLabel.grid(column=0, row=0)
        isbnEntry = ttk.Entry(self.tab, width=20, textvariable=isbn)
        isbnEntry.grid(column=1, row=0)

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
