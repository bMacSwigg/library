import random
from tkinter import *
from tkinter import ttk

from backend.models import User
from constants import *
from ui.tabs.base import BaseTab


class UsersTab(BaseTab):

    def _createUser(self):
        name = self.name.get()
        email = self.email.get()
        if all([name, email]):
            user_id = random.randint(MIN_USER_ID, MAX_USER_ID)
            user = User(user_id, name, email)
            self.bs.createUser(user)
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
    
    def _make(self):
        self.newuserframe = ttk.Frame(self.tab)
        self.newuserframe.pack(side='top', fill='x', expand=False)
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

        # A small abuse of Treeview to make a table...
        userslist = ttk.Treeview(self.tab, columns=('id', 'email'))
        userslist.heading('id', text='User ID')
        userslist.heading('email', text='Email')
        users = self.bs.listUsers()
        for u in users:
            userslist.insert('', 'end', u.user_id, text=u.name, values=(u.user_id, u.email))
        userslist.pack(side='bottom', fill='both', expand=True)
