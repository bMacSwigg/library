# TODO: give this a better class structure

import io
import PIL.ImageTk
import PIL.Image
from tkinter import *
from tkinter import ttk
import urllib.request

from backend.api import BookService, LookupService
from backend.models import Book
# Embarrassing for Tk that this needs a custom impl
from ui.scrollable import ScrollFrame

ERROR_STYLE = 'Error.TLabel'
TITLE_STYLE = 'Title.TLabel'
AUTHOR_STYLE = 'Author.TLabel'
METADATA_STYLE = 'Metadta.TLabel'

def imageFromUrl(url):
    try:
        with urllib.request.urlopen(url) as u:
            data = u.read()
        image = PIL.Image.open(io.BytesIO(data))
    except ValueError as e:
        # TODO: log the error and replace it with a default "error" img
        print(e)
        image = PIL.Image.new('RGB', (128,192), (0,0,0))
    return PIL.ImageTk.PhotoImage(image)

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

    def __init__(self, tab, bs):
        super().__init__(tab, bs)
        # Track references to ImageTk instances so they don't disappear
        self.imgs = []

    def _getBooks(self) -> list[Book]:
        return self.bs.listBooks()

    def _makeBookRow(self, book: Book, ind: int):
        imgFrame = ttk.Frame(self.booksframe)
        imgFrame.grid(column=0, row=ind, sticky=(N, W))
        img = imageFromUrl(book.thumbnail)
        self.imgs.append(img)
        imglabel = ttk.Label(imgFrame, image=img)
        imglabel.grid(column=0, row=0, sticky=(N, W))

        metadataFrame = ttk.Frame(self.booksframe)
        metadataFrame.grid(column=1, row=ind, sticky=(N, W))
        title = ttk.Label(metadataFrame, text=book.title)
        title.grid(column=0, row=0, columnspan=2, sticky=(N, W))
        title.configure(style=TITLE_STYLE)
        author = ttk.Label(metadataFrame, text=book.author)
        author.grid(column=0, row=1, sticky=W)
        author.configure(style=AUTHOR_STYLE)
        year = ttk.Label(metadataFrame, text=book.year)
        year.grid(column=1, row=1, sticky=W, padx=4)
        year.configure(style=METADATA_STYLE)
        isbn = ttk.Label(metadataFrame, text=('ISBN: %s' % book.isbn))
        isbn.grid(column=0, row=2, columnspan=2, sticky=W)
        isbn.configure(style=METADATA_STYLE)

        actionFrame = ttk.Frame(self.booksframe)
        actionFrame.grid(column=2, row=ind, sticky=E)
        checkout = ttk.Button(actionFrame, text="Checkout")
        checkout.grid(column=0, row=0)
        ret = ttk.Button(actionFrame, text="Return")
        ret.grid(column=0, row=1)

    def refresh(self):
        self.imgs = []
        super().refresh()

    def _make(self):
        scrollframe = ScrollFrame(self.tab)
        scrollframe.pack(side='top', fill='both', expand=True)
        self.booksframe = scrollframe.viewPort

        books = self._getBooks()
        for i,book in enumerate(books):
            self._makeBookRow(book, i)

class ImportTab(_BaseTab):

    def __init__(self, tab, bs, ls):
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
        if all([i, t, a, c, y, url]):
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
    
class AppWindow:

    def __init__(self):
        self.bs = BookService()
        self.ls = LookupService()

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
        ttk.Style().configure(AUTHOR_STYLE, font=('Arial', 10, 'italic'))
        ttk.Style().configure(METADATA_STYLE, font=('Arial', 10))

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
        self.importTab = ImportTab(tabImport, self.bs, self.ls)
        self.importTab.refresh()

        root.mainloop()
