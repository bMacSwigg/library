from tkinter import *
from tkinter import ttk
from tkinter.simpledialog import Dialog

class ComboBoxDialog(Dialog):

    def __init__(self, title: str, prompt: str, choices: list[str]):
        self.prompt = prompt
        self.choices = choices
        # self.val = None  # Will hold the return value, once chosen

        super().__init__(None, title)

    def destroy(self):
        self.combobox = None
        Dialog.destroy(self)

    def body(self, master):

        label = ttk.Label(master, text=self.prompt, justify=LEFT)
        label.grid(row=0, padx=5, sticky=W)
        
        self.combobox = ttk.Combobox(master, value=self.choices)  # TBD: readonly?
        self.combobox.grid(row=1, padx=5, sticky=W+E)

        return self.combobox

    def validate(self):
        self.result = self.combobox.get()
        return 1

def askcombo(title: str, prompt: str, choices: list[str]):
    return ComboBoxDialog(title, prompt, choices).result

if __name__ == '__main__':
    print(askcombo('Test', 'What is the answer?', ['Apple', 'Banana']))
