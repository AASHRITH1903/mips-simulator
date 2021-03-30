from pipelined import *
from pipelined_df import *

from tkinter import *

def a():
    p = Pipelined()
    p.run()

def b():
    pdf = Pipelined_DF()
    pdf.run()

root = Tk()
root.geometry("500x500")
root.title("MIPS pipeline simulator")

t = Text(root, width=500, height=1, wrap=WORD)
t.pack()
t.insert(END, "Select from this : \n")

b1 = Button(root, text="pipeline without data-forwarding", command=a).pack()
b2 = Button(root, text="pipeline with data-forwarding", command=b).pack()

root.mainloop()



