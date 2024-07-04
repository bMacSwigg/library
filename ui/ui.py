import io
from tkinter import *
from tkinter import ttk

from backend.api import BookService, LookupService
from constants import *
from ui.image_loader import CachedImageLoader
from ui.tabs.catalog import CatalogTab
from ui.tabs.circulation import CirculationTab
from ui.tabs.import_tab import ImportTab
from ui.tabs.users import UsersTab


class AppWindow:

    def __init__(self):
        self.bs = BookService()
        self.ls = LookupService()
        self.cil = CachedImageLoader()

    def refreshCurrentTab(self, event):
        ind = self.tabs.index('current')
        if ind == 0:
            self.catalogTab.refresh()
        elif ind == 1:
            self.circulationTab.refresh()
        elif ind == 2:
            self.importTab.refresh()
        elif ind == 3:
            self.usersTab.refresh()

    def main(self):
        root = Tk()
        root.title('Brian\'s Library')
        root.geometry('600x400')

        ttk.Style().configure(ERROR_STYLE, foreground='red')
        ttk.Style().configure(TITLE_STYLE, font=('Arial', 14, 'bold'))
        ttk.Style().configure(AUTHOR_STYLE, font=('Arial', 10, 'italic'))
        ttk.Style().configure(METADATA_STYLE, font=('Arial', 10))

        mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        self.tabs = ttk.Notebook(mainframe)
        tabCatalog = ttk.Frame(self.tabs)
        tabCirculation = ttk.Frame(self.tabs)
        tabImport = ttk.Frame(self.tabs)
        tabUsers = ttk.Frame(self.tabs)
        self.tabs.add(tabCatalog, text='Catalog')
        self.tabs.add(tabCirculation, text='Circulation')
        self.tabs.add(tabImport, text='Import')
        self.tabs.add(tabUsers, text='Users')
        self.tabs.pack(expand=1, fill='both')
        self.tabs.bind('<<NotebookTabChanged>>', self.refreshCurrentTab)

        self.catalogTab = CatalogTab(tabCatalog, self.bs, self.cil)
        self.circulationTab = CirculationTab(tabCirculation, self.bs, self.cil)
        self.importTab = ImportTab(tabImport, self.bs, self.ls)
        self.usersTab = UsersTab(tabUsers, self.bs)

        root.mainloop()
