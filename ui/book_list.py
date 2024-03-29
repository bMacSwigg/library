from tkinter import *
from tkinter import ttk

from backend.api import BookService
from backend.models import Book
from ui.book_details import BookDetails
from ui.image_loader import CachedImageLoader

class BookList:

    def __init__(self, frame: ttk.Frame, books: list[Book],
                 bs: BookService, cil: CachedImageLoader):
        self.frame = frame
        self.books = books
        self.bs = bs
        self.cil = cil

    def display(self, showLoadingBar: bool):
        if showLoadingBar:
            loadingframe = ttk.Frame(self.frame)
            loadingframe.grid(column=0, row=0)
            ttk.Label(loadingframe, text='Loading...').pack()
            # +1 because Tkinter can't show a full bar
            size = len(self.books) + 1
            progressbar = ttk.Progressbar(loadingframe, maximum=size)
            progressbar.pack()

        # Load data
        rows = []
        for i,book in enumerate(self.books):
            bd = BookDetails(self.frame, i, self.bs, book, self.cil)
            rows.append(bd)
            if showLoadingBar:
                progressbar.step(1)
                self.frame.update()

        if showLoadingBar:
            loadingframe.destroy()
        for book in rows:
            book.refresh()

    def destroy(self):
        for child in self.frame.winfo_children():
            child.destroy()
