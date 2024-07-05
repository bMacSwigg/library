from tkinter import *
from tkinter import ttk

from backend.api import BookService
from backend.db import Action
from constants import *
from ui.book_details import HistoricBookDetails
from ui.image_loader import CachedImageLoader
from ui.scrollable import ScrollFrame


class UserActivity:

    def __init__(self, bs: BookService, cil: CachedImageLoader, user_id: int):
        self.bs = bs
        self.cil = cil
        self.user = bs.getUser(user_id)

        self.root = Toplevel()
        self.root.geometry(POPUP_WINDOW_SIZE)
        self.root.title('User Activity: %s (%d)' % (self.user.name, user_id))
        scrollframe = ScrollFrame(self.root)
        scrollframe.pack(side='bottom', fill='both', expand=True)
        vp = scrollframe.viewPort

        out, back = self._partition_user_logs(user_id)

        out_label = ttk.Label(vp, text='Currently checked out')
        out_label.grid(column=0, row=0, sticky=W, pady=(0,10))
        out_label.configure(style=HEADER_STYLE)
        out_frame = ttk.Frame(vp)
        out_frame.grid(column=0, row=1, sticky=W)
        self.out_rows = self._display_outs(out_frame, out)

        back_label = ttk.Label(vp, text='Previously borrowed')
        back_label.grid(column=0, row=2, sticky=W, pady=(0,10))
        back_label.configure(style=HEADER_STYLE)
        back_frame = ttk.Frame(vp)
        back_frame.grid(column=0, row=3, sticky=W)
        self.back_rows = self._display_backs(back_frame, back)

        # This is... mostly just structured this way because we have to hold
        # onto a reference to the various rows, so Tkinter doesn't GC the images
        for r in (self.out_rows + self.back_rows):
            r.refresh()

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
        rows = []
        for idx, o in enumerate(out):
            book = self.bs.getBook(o[0][0])
            out_time = o[0][0]
            hbd = HistoricBookDetails(frame, idx, book, self.cil, out_time)
            rows.append(hbd)
        return rows

    def _display_backs(self, frame, back):
        rows = []
        for idx, b in enumerate(back):
            book = self.bs.getBook(b[0][0])
            out_time = b[0][1]
            ret_time = b[1][1]
            hbd = HistoricBookDetails(frame, idx, book, self.cil, out_time, ret_time)
            rows.append(hbd)
        return rows
