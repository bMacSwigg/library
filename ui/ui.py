# TODO: give this a better class structure

from tkinter import *
from tkinter import ttk

from backend.models import Book

def getBooks() -> list[Book]:
    return [Book('1234', 'Paul'), Book('5678', 'Babel')]

def makeBookRow(book: Book, ind: int, tab):
    row = ttk.Frame(tab)
    row.grid(column=0, row=ind, sticky=(W, E))
    ttk.Label(row, text=('Title: %s' % book.title)).grid(column=0, row=0, sticky=W)
    ttk.Label(row, text=('ISBN: %s' % book.isbn)).grid(column=1, row=0, sticky=E)

root = Tk()
root.title('Brian\'s Library')

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

tabs = ttk.Notebook(mainframe)
tabCatalog = ttk.Frame(tabs)
tabCheckout = ttk.Frame(tabs)
tabImport = ttk.Frame(tabs)
tabs.add(tabCatalog, text='Catalog')
tabs.add(tabCheckout, text='Checkout')
tabs.add(tabImport, text='Import')
tabs.pack(expand=1, fill='both')

books = getBooks()
for i,book in enumerate(books):
    print(i)
    makeBookRow(book, i, tabCatalog)

root.mainloop()
