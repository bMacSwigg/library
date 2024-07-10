from tkinter import *
from tkinter import ttk

from library.backend.api import BookService, UserService
from library.constants import *
from library.ui.image_loader import CachedImageLoader
from library.ui.tabs.base import BaseTab
from library.ui.user_activity import UserActivity


class UsersTab(BaseTab):

    def __init__(self, tab: ttk.Frame, bs: BookService, us: UserService,
                 cil: CachedImageLoader):
        super().__init__(tab, bs)
        self.us = us
        self.cil = cil
        self.ua_list = []

    def _createUser(self):
        name = self.name.get()
        email = self.email.get()
        if all([name, email]):
            self.us.createUser(name, email)
            self.refresh()
        else:
            self._showError('Missing properties')

    def _clearError(self):
        if hasattr(self, 'error') and self.error.winfo_exists():
            self.error.destroy()

    def _showError(self, msg):
        self._clearError()
        self.error = ttk.Label(self.newuserframe, text=('Error: %s' % msg))
        self.error.configure(style=ERROR_STYLE)
        self.error.grid(column=5, row=0)

    def _openUserDetails(self, event):
        for user_id in self.userslist.selection():
            ua = UserActivity(self.bs, self.us, self.cil, int(user_id))
            # We have to keep a handle on these, so tkinter doesn't GC the image
            # This produces a small leak, since we can't easily remove these
            # from the list, even after they've been closed
            self.ua_list.append(ua)

    def _make(self):
        # A small abuse of Treeview to make a table...
        self.userslist = ttk.Treeview(self.tab, columns=('id', 'email'))
        self.userslist.heading('id', text='User ID')
        self.userslist.heading('email', text='Email')
        users = self.us.listUsers()
        for u in users:
            self.userslist.insert('', 'end', u.user_id, text=u.name, values=(u.user_id, u.email))
        self.userslist.pack(side='top', fill='both', expand=True)
        self.userslist.bind('<Double-Button-1>', self._openUserDetails)
        self.userslist.bind('<Return>', self._openUserDetails)

        self.newuserframe = ttk.Frame(self.tab)
        self.newuserframe.pack(side='bottom', fill='x', expand=False)
        self.name = StringVar()
        nameLabel = ttk.Label(self.newuserframe, text="Name:")
        nameLabel.grid(column=0, row=0)
        nameEntry = ttk.Entry(self.newuserframe, width=20, textvariable=self.name)
        nameEntry.grid(column=1, row=0)
        self.email = StringVar()
        emailLabel = ttk.Label(self.newuserframe, text="Email:")
        emailLabel.grid(column=2, row=0)
        emailEntry = ttk.Entry(self.newuserframe, width=20, textvariable=self.email)
        emailEntry.grid(column=3, row=0)
        createbtn = ttk.Button(self.newuserframe, text='Create User', command=self._createUser)
        createbtn.grid(column=4, row=0)
