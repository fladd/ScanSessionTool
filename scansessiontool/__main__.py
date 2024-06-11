import os
import platform
from tkinter import *
from tkinter.ttk import *

from .scansessiontool import ScanSessionTool


def run():
    root = Tk()
    if platform.system() == "Windows":
        root.iconbitmap(os.path.abspath(os.path.join(
            os.path.split(__file__)[0], "sst_icon.ico")))
    else:
        root.tk.call('wm', 'iconphoto', root._w,
                     PhotoImage(file=os.path.abspath(os.path.join(
                os.path.split(__file__)[0], "sst_icon.png"))))
    app = ScanSessionTool(root)
    app.mainloop()

if __name__ == "__main__":
    run()
