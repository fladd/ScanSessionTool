""" Dialogues.

A set of Tkinter dialogues used in Scan Session Tool.

"""


import os
import platform

from tkinter import *
from tkinter import _tkinter
from tkinter.ttk import *
from tkinter import filedialog as tkFileDialog
from tkinter.scrolledtext import ScrolledText

from .widgets import FixedSizeFrame

class ArchiveDialogue:
    """Tkinter dialogue showing settings for archiving procedure."""

    def __init__(self, master):
        self.master = master
        top = self.top = Toplevel(master, background="grey85")
        top.title("Archive")
        top.resizable(False, False)

        self.data_frame = LabelFrame(top, text="Data", padding=(5,5))
        self.data_frame.grid(row=0, column=0, sticky="NSWE", padx=10, pady=10)
        self.data_frame.grid_columnconfigure(1, weight=1)
        self.source_label = Label(self.data_frame, text="Source:")
        self.source_label.grid(row=0, column=0, sticky="E", padx=(0, 3),
                               pady=3)
        self.source_var = StringVar()
        self.source_entry = Entry(self.data_frame, width=50,
                                  textvariable=self.source_var)
        self.source_entry["state"] = "readonly"
        self.source_entry.grid(row=0, column=1, sticky="W")
        self.source_button = Button(self.data_frame, text="Browse",
                                    command=self.set_source)
        self.source_button.grid(row=0, column=3, sticky="E")
        self.target_label = Label(self.data_frame, text="Target:")
        self.target_label.grid(row=1, column=0, sticky="E", padx=(0, 3),
                               pady=3)
        self.target_var = StringVar()
        self.target_entry = Entry(self.data_frame, width=50,
                                  textvariable=self.target_var)
        self.target_entry["state"] = "readonly"
        self.target_entry.grid(row=1, column=1, sticky="W")
        self.target_button = Button(self.data_frame, text="Browse",
                                    command=self.set_target)
        self.target_button.grid(row=1, column=3, sticky="E")

        self.options_frame = LabelFrame(top, text="Options", padding=(5,5))
        self.options_frame.grid(row=1, column=0, sticky="NSWE", padx=10)
        self.options_frame.grid_columnconfigure(1, weight=1)
        self.bv_links_var = IntVar()
        self.bv_links_var.set(0)
        self.bv_links_checkbox = Checkbutton(self.options_frame,
                                             text="Create BrainVoyager links",
                                             var=self.bv_links_var)
        self.bv_links_checkbox.grid(row=0, column=0, sticky="W")
        self.tbv_links_var = IntVar()
        self.tbv_links_var.set(0)
        self.tbv_links_checkbox = Checkbutton(
            self.options_frame,
            text="Create Turbo-BrainVoyager links",
            var=self.tbv_links_var,
            command=self.activate_tbv)
        self.tbv_links_checkbox.grid(row=1, column=0, sticky="W")
        self.tbv_files_label = Label(self.options_frame,
                                     text="TBV files directory name:")
        self.tbv_files_label["state"] = DISABLED
        self.tbv_files_label.grid(row=2, column=0, sticky="E", padx=(0, 3))
        self.tbv_files_var = StringVar()
        self.tbv_files_entry = Entry(self.options_frame,
                                     textvariable=self.tbv_files_var)
        self.tbv_files_var.set("TBVFiles")
        self.tbv_files_entry["state"] = DISABLED
        self.tbv_files_entry.grid(row=2, column=1, sticky="WE")
        self.tbv_prefix_label = Label(self.options_frame,
                                      text="Run prefix:")
        self.tbv_prefix_label["state"] = DISABLED
        self.tbv_prefix_label.grid(row=3, column=0, sticky="E", padx=(0, 3))
        self.tbv_prefix_var = StringVar()
        self.tbv_prefix_entry = Entry(self.options_frame,
                                      textvariable=self.tbv_prefix_var)
        self.tbv_prefix_var.set("TBV_")
        self.tbv_prefix_entry["state"] = DISABLED
        self.tbv_prefix_entry.grid(row=3, column=1, sticky="WE")

        self.okay_button = Button(top, text="GO", command=self.archive)
        self.okay_button["state"] = DISABLED
        self.okay_button.grid(row=2, column=0, pady=10)
        self.okay = False

        top.protocol("WM_DELETE_WINDOW", self.cancel)
        top.bind("<Escape>", self.cancel)

        top.geometry("+%d+%d" % (master.winfo_rootx(), master.winfo_rooty()))

        top.transient(self.master)
        top.focus_force()
        top.wait_visibility()
        top.grab_set()
        if platform.system() == "Windows":
            master.wm_attributes("-disabled", True)
        self.master.wait_window(self.top)

    def activate_tbv(self):
        if self.tbv_links_var.get() == 1:
            self.tbv_files_label["state"] = NORMAL
            self.tbv_files_entry["state"] = NORMAL
            self.tbv_prefix_label["state"] = NORMAL
            self.tbv_prefix_entry["state"] = NORMAL
        else:
            self.tbv_files_label["state"] = DISABLED
            self.tbv_files_entry["state"] = DISABLED
            self.tbv_prefix_label["state"] = DISABLED
            self.tbv_prefix_entry["state"] = DISABLED

    def set_source(self):
        d = tkFileDialog.askdirectory(parent=self.top,
            title="Select directory containing all raw data")
        if d not in ("", ()):
            self.source_var.set(os.path.abspath(d))
        if self.source_var.get() != "" and self.target_var.get() != "":
            self.okay_button["state"] = NORMAL

    def set_target(self):
        d = tkFileDialog.askdirectory(parent=self.top,
            title="Select target directory to archive data to")
        if d != "":
            self.target_var.set(os.path.abspath(d))
        if self.source_var.get() != "" and self.target_var.get() != "":
            self.okay_button["state"] = NORMAL

    def get(self):
        return (self.okay,
                self.source_var.get(),
                self.target_var.get(),
                self.bv_links_var.get(),
                self.tbv_links_var.get(),
                self.tbv_files_var.get(),
                self.tbv_prefix_var.get())

    def destroy(self):
        if platform.system() == "Windows":
            self.master.wm_attributes("-disabled", False)
        self.top.grab_release()
        self.top.destroy()

    def cancel(self, *args):
        self.okay = False
        self.destroy()

    def archive(self):
        self.okay = True
        self.destroy()


class BusyDialogue:
    """Tkinter dialogue showing progress information during data archiving."""

    def __init__(self, app):
        self.master = app.master
        top = self.top = Toplevel(self.master, background="#49d042")
        if platform.system() == "Linux":
            try:
                top.attributes('-type', 'splash')
            except:
                pass
        else:
            top.overrideredirect(True)

        style = Style()
        style.configure("Black.TFrame", background="#49d042")
        style.configure("White.TLabel", background="#49d042")
        self.frame = FixedSizeFrame(top, width=300, height=100,
                                    style="Black.TFrame")
        self.frame.grid()
        self.status1 = StringVar()
        self.label1 = Label(self.frame, textvariable=self.status1,
                           style="White.TLabel", justify=CENTER)
        self.label1['font'] = (app.default_font, app.default_font_size, "bold")
        self.label1.grid(row=0, column=0, padx=10, pady=(10,0))
        self.status2 = StringVar()
        self.label2 = Label(self.frame, textvariable=self.status2,
                           style="White.TLabel", justify=CENTER)
        self.label2['font'] = ("Arial", -13, "normal")
        self.label2.grid(row=1, column=0, padx=10, pady=(0,25))

        top.transient(self.master)
        top.focus_set()
        top.wait_visibility()
        top.grab_set()
        self.bind_id = self.master.bind("<Configure>", self.bring_to_top)
        if platform.system() == "Windows":
            self.master.wm_attributes("-disabled", True)
        self.bring_to_top()

    def update(self, event=None, status=None):

        if status is not None:
            self.status1.set(status[0])
            self.status2.set(status[1])

    def bring_to_top(self, *args):
        dx = self.master.winfo_width() / 2 - self.top.winfo_width() / 2
        dy = self.master.winfo_height() / 2 - self.top.winfo_height() / 2
        self.top.geometry("+%d+%d" % (self.master.winfo_rootx() + dx,
                                      self.master.winfo_rooty() + dy))
        self.top.update_idletasks()
        self.top.focus_set()
        self.top.lift()

    def destroy(self):
        if platform.system() == "Windows":
            self.master.wm_attributes("-disabled", False)
        self.master.focus_set()
        self.master.unbind("<Configure>", self.bind_id)
        self.top.destroy()


class MessageDialogue:
    """Tkinter dialogue showing log message of archiving procedure outcome."""

    def __init__(self, master, message):
        self.master = master
        top = self.top = Toplevel(master, background="grey85")
        top.title("Archiving Report")
        top.resizable(False, False)

        self.text = ScrolledText(top, width=77)
        self.text.pack()
        self.text.insert(END, message)
        self.text["state"] = "disabled"

        b = Button(top, text="OK", command=self.ok)
        b.pack(pady=10)

        top.protocol("WM_DELETE_WINDOW", self.ok)
        top.bind("<Escape>", self.ok)

        top.geometry("+%d+%d" % (master.winfo_rootx(), master.winfo_rooty()))

        top.transient(self.master)
        top.focus_force()
        top.wait_visibility()
        top.grab_set()
        if platform.system() == "Windows":
            master.wm_attributes("-disabled", True)

    def ok(self):
        if platform.system() == "Windows":
            self.master.wm_attributes("-disabled", False)
        self.top.grab_release()
        self.top.destroy()


class HelpDialogue:
    """Tkinter dialogue showing a text file with documentation."""

    def __init__(self, master):
        self.master = master
        top = self.top = Toplevel(master, background="grey85")
        top.title("Help")
        top.resizable(False, False)

        self.text = ScrolledText(top, width=77)
        self.text.pack()
        help_file = os.path.join(os.path.split(__file__)[0], "help.txt")
        self.text.insert(END, open(help_file).read())
        self.text["state"] = "disabled"
        b = Button(top, text="OK", command=self.ok)
        b.pack(pady=5)

        top.protocol("WM_DELETE_WINDOW", self.ok)
        top.bind("<Escape>", self.ok)

        top.geometry("+%d+%d" % (master.winfo_rootx(), master.winfo_rooty()))

        top.transient(self.master)
        top.focus_force()
        top.wait_visibility()
        top.grab_set()
        if platform.system() == "Windows":
            master.wm_attributes("-disabled", True)
        master.wait_window(top)

    def ok(self, *args):
        if platform.system() == "Windows":
            self.master.wm_attributes("-disabled", False)
        self.top.grab_release()
        self.top.destroy()
