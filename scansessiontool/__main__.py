import sys
import platform

if sys.version[0] == '3':
    from tkinter import *
    from tkinter.ttk import *
else:
    from Tkinter import *
    from ttk import *

from .scansessiontool import ScanSessionTool


def run():
    root = Tk()
    style = Style()
    style.theme_use("default")
    root.resizable(False, False)
    root.option_add('*tearOff', FALSE)
    app = ScanSessionTool(master=root)
    app.set_title()
    if platform.system() == "Darwin":
        root.bind('<Command-q>', app.quit_callback)
    root.bind('<Escape>', lambda x: app.master.focus())
    app.bind('<Button-1>', lambda x: app.master.focus())
    for label in app.nofocus_widgets:
        label.bind('<Button-1>', lambda x: app.master.focus())
    root.protocol("WM_DELETE_WINDOW", app.quit_callback)
    app.general_widgets[0].focus()
    app.disable_save()
    app.mouseover_callback(True)
    app.mainloop()


if __name__ == "__main__":
    run()
