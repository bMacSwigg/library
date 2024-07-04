from tkinter import ttk

from backend.api import BookService
from backend.models import Book
from ui.book_list import BookList
from ui.hinted_entry import HintedEntry, HintedStringVar
from ui.image_loader import CachedImageLoader
from ui.scrollable import ScrollFrame
from ui.tabs.base import BaseTab

class CatalogTab(BaseTab):
    """Main tab, for showing the full catalog & searching for books"""

    def __init__(self, tab: ttk.Frame, bs: BookService, cil: CachedImageLoader):
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
