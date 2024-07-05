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

        out, back = self._partition_user_logs(user_id)

        out_label = ttk.Label(self.root, text='Currently checked out')
        out_label.grid(column=0, row=0, sticky=W)
        out_frame = ttk.Frame(self.root)
        out_frame.grid(column=0, row=1)
        self._display_outs(out_frame, out)

        back_label = ttk.Label(self.root, text='Previously borrowed')
        back_label.grid(column=0, row=2, sticky=W)
        back_frame = ttk.Frame(self.root)
        back_frame.grid(column=0, row=3)
        self._display_backs(back_frame, back)

    def _partition_user_logs(self, user_id: int) -> tuple[list, list]:
        logs = self.bs.listUserCheckoutHistory(user_id)
        # list of logs will be ordered by timestamp
        # if a book was checked out, it cannot be checked out again until returned
        # and the return will be associated with the same user
        # so we can take each checkout & find the next matching return (if any)
        checkouts = filter(lambda l: l[2] == Action.CHECKOUT.value, logs)
        returns = list(filter(lambda l: l[2] == Action.RETURN.value, logs))
        pairs = list(map(lambda c: (c, self._find_return(c, returns)), checkouts))

        out = list(filter(lambda p: p[1] is None, pairs))
        back = list(filter(lambda p: p[1] is not None, pairs))
        return out, back

    def _find_return(self, checkout, returns):
        matching = filter(lambda r: r[0] == checkout[0], returns)
        return next(filter(lambda r: r[1] > checkout[1], matching), None)

    def _display_outs(self, frame, out):
        for idx, o in enumerate(out):
            book = self.bs.getBook(o[0][0])
            txt = ('Checked out \'%s\' at %s' % (book.title, o[0][1]))
            label = ttk.Label(frame, text=txt, wraplength=440)
            label.grid(column=0, row=idx, sticky=W, ipady=4, ipadx=4)

    def _display_backs(self, frame, back):
        for idx, b in enumerate(back):
            book = self.bs.getBook(b[0][0])
            txt = ('Checked out \'%s\' at %s, returned at %s' %
                   (book.title, b[0][1], b[1][1]))
            label = ttk.Label(frame, text=txt, wraplength=440)
            label.grid(column=0, row=idx, sticky=W, ipady=4, ipadx=4)
