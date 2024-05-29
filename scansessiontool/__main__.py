import platform
from tkinter import *
from tkinter.ttk import *

from .scansessiontool import ScanSessionTool


if __name__ == "__main__":
    root = Tk()
    app = ScanSessionTool(root)
    app.mainloop()
