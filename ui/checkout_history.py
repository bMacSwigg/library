from tkinter import *
from tkinter import ttk

from backend.api import BookService
from backend.db import Action
from backend.models import Book
from ui.image_loader import CachedImageLoader

class CheckoutHistory:

    def __init__(self, bs: BookService, book: Book):
        self.bs = bs
        self.book = book

        self.root = Toplevel()
        self.root.geometry("480x320")
        self.root.title("Checkout History: %s" % book.title)

        logs = self.bs.listBookCheckoutHistory(book.isbn)
        for idx, log in enumerate(logs):
            if log[0] == Action.CHECKOUT.value:
                self._checkout(idx, log[1], log[2])
            else:
                self._return(idx, log[2])

        self.root.mainloop()

    def _checkout(self, idx, user, time):
        txt = ('Checked out by %s at %s' % (user, time))
        label = ttk.Label(self.root, text=txt, wraplength=440)
        label.grid(column=0, row=idx, sticky=W, ipady=4, ipadx=4)

    def _return(self, idx, time):
        txt = ('Returned at %s' % time)
        label = ttk.Label(self.root, text=txt, wraplength=440)
        label.grid(column=0, row=idx, sticky=W, ipady=4, ipadx=4)
