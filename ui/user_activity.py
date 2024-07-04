from tkinter import *
from tkinter import ttk

from backend.api import BookService
from backend.db import Action
from constants import *


class UserActivity:

    def __init__(self, bs: BookService, user_id: int):
        self.bs = bs
        self.user = bs.getUser(user_id)

        self.root = Toplevel()
        self.root.geometry(POPUP_WINDOW_SIZE)
        self.root.title('User Activity: %s (%d)' % (self.user.name, user_id))

        logs = bs.listUserCheckoutHistory(user_id)
        # TODO: This can be displayed much better
        # group by book, separate currently-out from returned, show covers
        for idx, log in enumerate(logs):
            if log[2] == Action.CHECKOUT.value:
                self._checkout(idx, log[0], log[1])
            else:
                self._return(idx, log[0], log[1])

    def _checkout(self, idx, isbn, time):
        book = self.bs.getBook(isbn)
        txt = ('Checked out \'%s\' at %s' % (book.title, time))
        label = ttk.Label(self.root, text=txt, wraplength=440)
        label.grid(column=0, row=idx, sticky=W, ipady=4, ipadx=4)

    def _return(self, idx, isbn, time):
        book = self.bs.getBook(isbn)
        txt = ('Returned \'%s\' at %s' % (book.title, time))
        label = ttk.Label(self.root, text=txt, wraplength=440)
        label.grid(column=0, row=idx, sticky=W, ipady=4, ipadx=4)
