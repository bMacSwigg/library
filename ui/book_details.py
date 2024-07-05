import io
import PIL.ImageTk
import PIL.Image
from tkinter import *
from tkinter import ttk
from tkinter.messagebox import askokcancel
from tkinter.simpledialog import askstring
import urllib.request

from backend.api import BookService
from backend.models import Book
from constants import *
from ui.checkout_history import CheckoutHistory
from ui.combobox_dialog import askcombo
from ui.image_loader import CachedImageLoader


class BasicBookDetails:

    def __init__(self, frame: ttk.Frame, ind: int, book: Book,
                 cil: CachedImageLoader):
        self.frame = frame
        self.ind = ind
        self.book = book
        self.cil = cil
        self.img = PIL.ImageTk.PhotoImage(cil.getImage(book.thumbnail))
        self.frames = []

    def refresh(self):
        for frame in self.frames:
            frame.destroy()
        self._make()

    def _displayCheckoutInfo(self, frame: ttk.Frame):
        # To be overridden by subclasses
        return

    def _make(self):
        imgFrame = ttk.Frame(self.frame)
        imgFrame.grid(column=0, row=self.ind, sticky=(N, W))
        imglabel = ttk.Label(imgFrame, image=self.img)
        imglabel.grid(column=0, row=0, sticky=(N, W))

        metadataFrame = ttk.Frame(self.frame)
        metadataFrame.grid(column=1, row=self.ind, sticky=(N, W))
        title = ttk.Label(metadataFrame, text=self.book.title,
                          wraplength=300)
        title.grid(column=0, row=0, sticky=(N, W))
        title.configure(style=TITLE_STYLE)
        author = ttk.Label(metadataFrame, text=self.book.author)
        author.grid(column=0, row=1, sticky=W)
        author.configure(style=AUTHOR_STYLE)
        year = ttk.Label(metadataFrame, text=self.book.year)
        year.grid(column=0, row=2, sticky=W)
        year.configure(style=METADATA_STYLE)
        isbn = ttk.Label(metadataFrame, text=('ISBN: %s' % self.book.isbn))
        isbn.grid(column=0, row=3, sticky=W)
        isbn.configure(style=METADATA_STYLE)
        self._displayCheckoutInfo(metadataFrame)

        self.frames = [imgFrame, metadataFrame]


class InteractiveBookDetails(BasicBookDetails):

    def __init__(self, frame: ttk.Frame, ind: int, book: Book,
                 cil: CachedImageLoader, bs: BookService):
        super().__init__(frame, ind, book, cil)
        self.bs = bs

    def _checkout(self):
        users = {('%s (%d)' % (u.name, u.user_id)):u
                 for u in self.bs.listUsers()}
        
        prompt = ('Who is checking out \'%s\'?' % self.book.title)
        user = askcombo('Checkout', prompt, list(users))
        if user is not None:
            self.bs.checkoutBook(self.book.isbn, users[user])
            self.refresh()

    def _return(self):
        prompt = ('Confirm: Return \'%s\'?' % self.book.title)
        confirm = askokcancel('Return', prompt)
        if confirm:
            self.bs.returnBook(self.book.isbn)
            self.refresh()

    def _history(self):
        CheckoutHistory(self.bs, self.book)

    def _displayCheckoutInfo(self, frame: ttk.Frame):
        if self.book.is_out:
            checkout_txt = ('Checked out by %s at %s' %
                            (self.book.checkout_user, self.book.checkout_time))
            checkout = ttk.Label(frame, text=checkout_txt, wraplength=300)
            checkout.grid(column=0, row=4, sticky=W, ipady=4)
            checkout.configure(style=METADATA_STYLE)

    def refresh(self):
        self.book = self.bs.getBook(self.book.isbn)
        super().refresh()

    def _make(self):
        super()._make()
        actionFrame = ttk.Frame(self.frame)
        actionFrame.grid(column=2, row=self.ind, sticky=E)
        if self.book.is_out:
            ret = ttk.Button(actionFrame, text="Return", command=self._return)
            ret.grid(column=0, row=0)
        else:
            checkout = ttk.Button(actionFrame, text="Checkout",
                                  command=self._checkout)
            checkout.grid(column=0, row=0)
        history = ttk.Button(actionFrame, text="History", command=self._history)
        history.grid(column=0, row=1)

        self.frames += [actionFrame]


class HistoricBookDetails(BasicBookDetails):

    def __init__(self, frame: ttk.Frame, ind: int, book: Book,
                 cil: CachedImageLoader, out_time: str,
                 ret_time: str|None = None):
        super().__init__(frame, ind, book, cil)
        print(book.thumbnail)
        print(self.img)
        self.out_time = out_time
        self.ret_time = ret_time

    def _displayCheckoutInfo(self, frame: ttk.Frame):
        checkout_txt = ('Checked out at %s' % self.out_time)
        checkout = ttk.Label(frame, text=checkout_txt, wraplength=300)
        checkout.grid(column=0, row=4, sticky=W, ipady=4)
        checkout.configure(style=METADATA_STYLE)
        if self.ret_time is not None:
            ret_txt = ('Returned at %s' % self.ret_time)
            ret = ttk.Label(frame, text=ret_txt, wraplength=300)
            ret.grid(column=0, row=5, sticky=W)
            ret.configure(style=METADATA_STYLE)

    def _make(self):
        super()._make()
        print(self.frames)


# TODO: Get this working
if __name__ == '__main__':
    bs = BookService()
    cil = CachedImageLoader()
    book = Book('9780063021426', 'Babel', 'R. F. Kuang', 'Fiction', '2022',
                'http://books.google.com/books/content?id=rkO-zgEACAAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api',
                True, 'Brian', 'Sometime')

    root = Tk()
    frame = ttk.Frame(root)
    bd = BookDetails(frame, 0, bs, book, cil)
    bd.refresh()
    root.mainloop()
