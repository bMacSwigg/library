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


class BookDetails:

    def __init__(self, frame: ttk.Frame, ind: int, bs: BookService, book: Book,
                 cil: CachedImageLoader):
        self.frame = frame
        self.ind = ind
        self.bs = bs
        self.book = book
        self.cil = cil
        self.img = PIL.ImageTk.PhotoImage(cil.getImage(book.thumbnail))
        self.frames = []

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
        if self.book.is_out:
            checkout_txt = ('Checked out by %s at %s' %
                            (self.book.checkout_user, self.book.checkout_time))
            checkout = ttk.Label(metadataFrame, text=checkout_txt, wraplength=300)
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
        history = ttk.Button(actionFrame, text="History", command=self._history)
        history.grid(column=0, row=1)

        self.frames = [imgFrame, metadataFrame, actionFrame]

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
