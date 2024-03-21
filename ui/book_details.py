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


def imageFromUrl(url):
    try:
        with urllib.request.urlopen(url) as u:
            data = u.read()
        image = PIL.Image.open(io.BytesIO(data))
    except ValueError as e:
        if url:
            # If the URL was empty, this is expected, so no point logging
            # TODO: log the error instead of just printing it
            print(e)
        image = PIL.Image.new('RGB', (128,192), (0,0,0))
    return PIL.ImageTk.PhotoImage(image)


class BookDetails:

    def __init__(self, frame: ttk.Frame, ind: int, bs: BookService, book: Book):
        self.frame = frame
        self.ind = ind
        self.bs = bs
        self.book = book
        self.img = imageFromUrl(book.thumbnail)
        self.frames = []
        self._make()

    def _checkout(self):
        prompt = ('Who is checking out \'%s\'?' % self.book.title)
        user = askstring('Checkout', prompt)
        if user is not None:
            self.bs.checkoutBook(self.book.isbn, user)
            self.refresh()

    def _return(self):
        prompt = ('Confirm: Return \'%s\'?' % self.book.title)
        confirm = askokcancel('Return', prompt)
        if confirm:
            self.bs.returnBook(self.book.isbn)
            self.refresh()

    def refresh(self):
        for frame in self.frames:
            frame.destroy()
        self.book = self.bs.getBook(self.book.isbn)
        self._make()

    def _make(self):
        imgFrame = ttk.Frame(self.frame)
        imgFrame.grid(column=0, row=self.ind, sticky=(N, W))
        imglabel = ttk.Label(imgFrame, image=self.img)
        imglabel.grid(column=0, row=0, sticky=(N, W))

        metadataFrame = ttk.Frame(self.frame)
        metadataFrame.grid(column=1, row=self.ind, sticky=(N, W))
        title = ttk.Label(metadataFrame, text=self.book.title)
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
        if self.book.is_out:
            checkout_txt = ('Checked out by %s at %s' %
                            (self.book.checkout_user, self.book.checkout_time))
            checkout = ttk.Label(metadataFrame, text=checkout_txt)
            checkout.grid(column=0, row=4, sticky=W, ipady=4)
            checkout.configure(style=METADATA_STYLE)

        actionFrame = ttk.Frame(self.frame)
        actionFrame.grid(column=2, row=self.ind, sticky=E)
        if self.book.is_out:
            ret = ttk.Button(actionFrame, text="Return", command=self._return)
            ret.grid(column=0, row=0)
        else:
            checkout = ttk.Button(actionFrame, text="Checkout",
                                  command=self._checkout)
            checkout.grid(column=0, row=0)

        self.frames = [imgFrame, metadataFrame, actionFrame]
