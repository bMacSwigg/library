from tkinter import ttk

from backend.api import BookService


class BaseTab:
    """Base class for top-level UI tabs"""

    def __init__(self, tab: ttk.Frame, bs: BookService):
        self.tab = tab
        self.bs = bs

    def _make(self):
        pass

    def refresh(self):
        for child in self.tab.winfo_children():
            child.destroy()
        self._make()
