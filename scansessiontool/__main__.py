import platform
from tkinter import *
from tkinter.ttk import *

from .scansessiontool import ScanSessionTool


def run():
    root = Tk()
    app = ScanSessionTool(root)
    app.mainloop()

if __name__ == "__main__":
    run()
