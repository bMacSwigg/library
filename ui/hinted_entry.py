import tkinter as tk
from tkinter import ttk

class HintedEntry(ttk.Entry):
    """An Entry subclass that will display a hint text when empty & unfocused
    """
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # TODO: handle gracefully if this arg is missing, or not Hinted
        textvar = kwargs['textvariable']
        self.bind('<FocusIn>', textvar.takeFocus)
        self.bind('<FocusOut>', textvar.giveFocus)


class HintedStringVar(tk.StringVar):
    """A StringVar subclass that will display a hint text when empty"""

    def __init__(self, hint):
        super().__init__()
        self.hint = hint
        self.set(hint)

    # override
    def get(self):
        val = super().get()
        if val == self.hint:
            return ''
        else:
            return val

    def takeFocus(self, e):
        if super().get() == self.hint:
            self.set('')

    def giveFocus(self, e):
        if super().get() == '':
            self.set(self.hint)


    
