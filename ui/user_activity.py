from tkinter import *
from tkinter import ttk

from library.backend.api import BookService, UserService
from library.backend.models import Action, LogEntry
from library.constants import *
from library.ui.book_details import HistoricBookDetails
from library.ui.image_loader import CachedImageLoader
from library.ui.scrollable import ScrollFrame


class UserActivity:

    def __init__(self, bs: BookService, us: UserService,
                 cil: CachedImageLoader, user_id: int):
        self.bs = bs
        self.cil = cil
        self.user = us.getUser(user_id)

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
        # Returns two lists:
        # - The first is books currently checked out, formatted as (LogEntry, None)
        # - The second is books previously checked out & returned, as (LogEntry, LogEntry)
        logs = self.bs.listUserCheckoutHistory(user_id)
        # list of logs will be ordered by timestamp
        # if a book was checked out, it cannot be checked out again until returned
        # and the return will be associated with the same user
        # so we can take each checkout & find the next matching return (if any)
        checkouts = filter(lambda l: l.action == Action.CHECKOUT, logs)
        returns = list(filter(lambda l: l.action == Action.RETURN, logs))
        pairs = list(map(lambda c: (c, self._find_return(c, returns)), checkouts))

        by_checkout_time = lambda p: p[0].timestamp
        pairs.sort(reverse=True, key=by_checkout_time)

        out = list(filter(lambda p: p[1] is None, pairs))
        back = list(filter(lambda p: p[1] is not None, pairs))
        return out, back

    def _find_return(self, checkout: LogEntry, returns: list[LogEntry]) -> LogEntry:
        matching = filter(lambda r: r.isbn == checkout.isbn, returns)
        return next(filter(lambda r: r.timestamp > checkout.timestamp, matching), None)

    def _display_outs(self, frame: ttk.Frame, out: list[tuple[LogEntry, None]]):
        rows = []
        for idx, o in enumerate(out):
            book = self.bs.getBook(o[0].isbn)
            out_time = o[0].timestamp
            hbd = HistoricBookDetails(frame, idx, book, self.cil, out_time)
            rows.append(hbd)
        return rows

    def _display_backs(self, frame: ttk.Frame, back: list[tuple[LogEntry, LogEntry]]):
        rows = []
        for idx, b in enumerate(back):
            book = self.bs.getBook(b[0].isbn)
            out_time = b[0].timestamp
            ret_time = b[1].timestamp
            hbd = HistoricBookDetails(frame, idx, book, self.cil, out_time, ret_time)
            rows.append(hbd)
        return rows
