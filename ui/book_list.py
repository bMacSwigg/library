from tkinter import *
from tkinter import ttk

from backend.api import BookService, UserService
from backend.models import Book
from ui.book_details import InteractiveBookDetails
from ui.image_loader import CachedImageLoader

class BookList:

    def __init__(self, frame: ttk.Frame, books: list[Book], bs: BookService,
                 us: UserService, cil: CachedImageLoader):
        self.frame = frame
        self.books = books
        self.bs = bs
        self.us = us
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
            bd = InteractiveBookDetails(self.frame, i, book, self.cil, self.bs, self.us)
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
