# TODO: give this a better class structure

import io
import PIL.ImageTk
import PIL.Image
import random
from tkinter import *
from tkinter import ttk
from tkinter.messagebox import askokcancel
from tkinter.simpledialog import askstring
import urllib.request

from backend.api import BookService, LookupService, NotFoundException
from backend.models import Book, User
from constants import *
from ui.book_list import BookList
from ui.hinted_entry import HintedEntry, HintedStringVar
from ui.image_loader import CachedImageLoader
# Embarrassing for Tk that this needs a custom impl
from ui.scrollable import ScrollFrame


class _BaseTab:

    def __init__(self, tab: ttk.Frame, bs: BookService):
        self.tab = tab
        self.bs = bs

    def _make(self):
        pass

    def refresh(self):
        for child in self.tab.winfo_children():
            child.destroy()
        self._make()


class CatalogTab(_BaseTab):

    def __init__(self, tab, bs, cil):
        super().__init__(tab, bs)
        self.cil = cil
        self.initialLoad = True
        self.books = None
        self.query = HintedStringVar('Title or author...')

    def _getBooks(self) -> list[Book]:
        return self.bs.listBooks(self.query.get())

    def refresh(self):
        if self.books:
            self.books.destroy()
        super().refresh()

    def _make(self):
        searchframe = ttk.Frame(self.tab)
        searchframe.pack(side='top', fill='x', expand=False)
        searchentry = HintedEntry(searchframe, width=20, textvariable=self.query)
        searchentry.bind('<Return>', lambda e: self.refresh())
        searchentry.pack(side='left')
        searchbtn = ttk.Button(searchframe, text='Search', command=self.refresh)
        searchbtn.pack(side='left')
        
        scrollframe = ScrollFrame(self.tab)
        scrollframe.pack(side='bottom', fill='both', expand=True)
        self.books = BookList(scrollframe.viewPort, self._getBooks(),
                              self.bs, self.cil)
        self.books.display(self.initialLoad)
        self.initialLoad = False


class CirculationTab(_BaseTab):

    def __init__(self, tab, bs, cil):
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

    def _showError(self, msg):
        self._clearError()
        self.error = ttk.Label(self.lookupframe, text=('Error: %s' % msg))
        self.error.configure(style=ERROR_STYLE)
        self.error.grid(column=3, row=0)

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


class UsersTab(_BaseTab):

    def _createUser(self):
        name = self.name.get()
        email = self.email.get()
        if all([name, email]):
            user_id = random.randint(MIN_USER_ID, MAX_USER_ID)
            user = User(user_id, name, email)
            self.bs.createUser(user)
            self.refresh()
        else:
            self._showError('Missing properties')

    def _clearError(self):
        if hasattr(self, 'error') and self.error.winfo_exists():
            self.error.destroy()

    def _showError(self, msg):
        self._clearError()
        self.error = ttk.Label(self.newuserframe, text=('Error: %s' % msg))
        self.error.configure(style=ERROR_STYLE)
        self.error.grid(column=5, row=0)
    
    def _make(self):
        self.newuserframe = ttk.Frame(self.tab)
        self.newuserframe.pack(side='top', fill='x', expand=False)
        self.name = StringVar()
        nameLabel = ttk.Label(self.newuserframe, text="Name:")
        nameLabel.grid(column=0, row=0)
        nameEntry = ttk.Entry(self.newuserframe, width=20, textvariable=self.name)
        nameEntry.grid(column=1, row=0)
        self.email = StringVar()
        emailLabel = ttk.Label(self.newuserframe, text="Email:")
        emailLabel.grid(column=2, row=0)
        emailEntry = ttk.Entry(self.newuserframe, width=20, textvariable=self.email)
        emailEntry.grid(column=3, row=0)
        createbtn = ttk.Button(self.newuserframe, text='Create User', command=self._createUser)
        createbtn.grid(column=4, row=0)

        # A small abuse of Treeview to make a table...
        userslist = ttk.Treeview(self.tab, columns=('id', 'email'))
        userslist.heading('id', text='User ID')
        userslist.heading('email', text='Email')
        users = self.bs.listUsers()
        for u in users:
            userslist.insert('', 'end', u.user_id, text=u.name, values=(u.user_id, u.email))
        userslist.pack(side='bottom', fill='both', expand=True)


class AppWindow:

    def __init__(self):
        self.bs = BookService()
        self.ls = LookupService()
        self.cil = CachedImageLoader()

    def refreshCurrentTab(self, event):
        ind = self.tabs.index('current')
        if ind == 0:
            self.catalogTab.refresh()
        elif ind == 1:
            self.circulationTab.refresh()
        elif ind == 2:
            self.importTab.refresh()
        elif ind == 3:
            self.usersTab.refresh()

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

        self.tabs = ttk.Notebook(mainframe)
        tabCatalog = ttk.Frame(self.tabs)
        tabCirculation = ttk.Frame(self.tabs)
        tabImport = ttk.Frame(self.tabs)
        tabUsers = ttk.Frame(self.tabs)
        self.tabs.add(tabCatalog, text='Catalog')
        self.tabs.add(tabCirculation, text='Circulation')
        self.tabs.add(tabImport, text='Import')
        self.tabs.add(tabUsers, text='Users')
        self.tabs.pack(expand=1, fill='both')
        self.tabs.bind('<<NotebookTabChanged>>', self.refreshCurrentTab)

        self.catalogTab = CatalogTab(tabCatalog, self.bs, self.cil)
        self.circulationTab = CirculationTab(tabCirculation, self.bs, self.cil)
        self.importTab = ImportTab(tabImport, self.bs, self.ls)
        self.usersTab = UsersTab(tabUsers, self.bs)

        root.mainloop()
