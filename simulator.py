from tkinter import *
from tkinter.filedialog import askopenfile

filename = ""
root = Tk()
def open_file():
    global filename
    filename = askopenfile()

def display():
    l = Label(root,text=filename.name).pack()


open_button = Button(root,text="open a file",command=open_file)
open_button.pack()

start_button = Button(root,text="start",command=display)
start_button.pack()

root.mainloop()