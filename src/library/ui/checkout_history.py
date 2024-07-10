from tkinter import *
from tkinter import ttk

from library.backend.api import BookService
from library.backend.models import Book, Action
from library.constants import *
from library.ui.image_loader import CachedImageLoader

class CheckoutHistory:

    def __init__(self, bs: BookService, book: Book):
        self.bs = bs
        self.book = book

        self.root = Toplevel()
        self.root.geometry(POPUP_WINDOW_SIZE)
        self.root.title('Checkout History: %s' % book.title)

        logs = self.bs.listBookCheckoutHistory(book.isbn)
        for idx, log in enumerate(logs):
            if log.action == Action.CHECKOUT:
                self._checkout(idx, log.user_name, log.timestamp)
            else:
                self._return(idx, log.timestamp)

    def _checkout(self, idx, user, time):
        txt = ('Checked out by %s at %s' % (user, time))
        label = ttk.Label(self.root, text=txt, wraplength=440)
        label.grid(column=0, row=idx, sticky=W, ipady=4, ipadx=4)

    def _return(self, idx, time):
        txt = ('Returned at %s' % time)
        label = ttk.Label(self.root, text=txt, wraplength=440)
        label.grid(column=0, row=idx, sticky=W, ipady=4, ipadx=4)
