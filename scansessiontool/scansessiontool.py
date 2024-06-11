"""Scan Session Tool.

A tool for MR scan session documentation and data archiving.

"""


import os
import platform
import time
import glob
import json
import shutil
import threading
import multiprocessing

from tkinter import *
from tkinter.ttk import *
from tkinter import _tkinter
from tkinter import font as tkFont
from tkinter import filedialog as tkFileDialog
from tkinter import messagebox as tkMessageBox
from tkinter.scrolledtext import ScrolledText

import yaml

from .__meta__ import __version__, __date__
from .widgets import (FixedSizeFrame,
                      AutoScrollbarText,
                      VerticalScrolledFrame,
                      AutocompleteCombobox,
                      Spinbox)
from .dialogues import (ArchiveDialogue,
                        BusyDialogue,
                        MessageDialogue,
                        HelpDialogue)
from .utilities import (replace,
                        readdicom)


class ScanSessionTool(Frame):
    """The main Scan Session Tool Tkinter application."""

    def __init__(self, master, run_actions=None):
        """Initialize the application.

        Parameters
        ----------
        master : Tkinter.TK instance
            the Tk root window
        run_actions : dict, optional
            when set, this runs specified actions right after starting and
            exits when finished; actions to run can be specified in the form
                "action": [value1, value2, ...]
            where "action" is the name of a method to run and "valueX" is a
            value that method usually gets via user interaction; the target
            method needs to specifically implement this feature (and only few
            do); currently this feature is mainly used for implementing
            automated tests; (default=None)

        """

        Frame.__init__(self, master)

        self.run_actions = run_actions

        self.master.withdraw()

        # Change application icon
        if platform.system() == "Windows":
            self.master.iconbitmap(os.path.abspath(os.path.join(
                os.path.split(__file__)[0], "sst_icon.ico")))
        else:
            self.master.tk.call(
                'wm', 'iconphoto', self.master._w,
                PhotoImage(file=os.path.abspath(os.path.join(
                    os.path.split(__file__)[0], "sst_icon.png"))))

        font = tkFont.nametofont("TkDefaultFont")
        font.config(family="Arial", size=-13)
        self.default_font = font.cget("family")
        self.default_font_size = font.cget("size")
        self.font = (self.default_font, self.default_font_size)

        style = Style()
        style.theme_use("default")
        self.red = "#fc625d"
        self.orange = "#fdbc40"
        style.configure("Blue.TLabel", foreground="royalblue")
        style.configure("Grey.TLabel", foreground="darkgrey")
        style.configure("Header.TLabel", background="darkgrey")
        style.configure("Header.TFrame", background="darkgrey")
        style.configure("Red.TCombobox", fieldbackground=self.red)
        style.configure("Orange.TCombobox", fieldbackground=self.orange)
        style.map("Orange.TCombobox", fieldbackground=[("readonly",
                                                        self.orange)])
        style.configure("Red.TEntry", fieldbackground=self.red)
        style.configure("Orange.TEntry", fieldbackground=self.orange)
        style.configure("Orange.TSpinbox", fieldbackground=self.orange)
        style.map("Orange.TSpinbox", fieldbackground=[("disabled",
                                                       self.orange)])

        self.master.option_add('*tearOff', FALSE)
        self.menubar = Menu(self.master)
        if platform.system() == "Darwin":
            modifier = "Command"
            self.apple_menu = Menu(self.menubar, name="apple")
            self.menubar.add_cascade(menu=self.apple_menu)
            self.apple_menu.add_command(
                label="About Scan Session Tool",
                command=lambda: HelpDialogue(self.master))
        else:
            modifier = "Control"
        self.file_menu = Menu(self.menubar)
        self.menubar.add_cascade(menu=self.file_menu, label="File")
        self.file_menu.add_command(label="Open", command=self.open,
                                   accelerator="{0}-O".format(modifier))
        self.master.bind("<{0}-o>".format(modifier), self.open)
        self.file_menu.add_command(label="Save", command=self.save,
                                   accelerator="{0}-S".format(modifier))
        self.file_menu.add_command(label="Archive", command=self.archive,
                                   accelerator="{0}-R".format(modifier))
        self.edit_menu = Menu(self.menubar)
        self.menubar.add_cascade(menu=self.edit_menu, label="Edit")
        self.edit_menu.add_command(label="Add Measurement",
                                   command=self.new_measurement,
                                   accelerator="{0}-M".format(modifier))
        self.master.bind("<{0}-m>".format(modifier), self.new_measurement)
        self.edit_menu.add_command(label="Delete Measurement",
                                   command=self.del_measurement,
                                   accelerator="{0}-D".format(modifier))
        self.master.bind("<{0}-d>".format(modifier), self.del_measurement)
        self.edit_menu.add_command(
            label="Scroll Measurements Up",
            command=lambda: app.measurements_frame.canvas.yview_scroll(
                -2, "units"),
            accelerator="{0}-Up".format(modifier))
        self.master.bind(
            "<{0}-Up>".format(modifier),
            lambda x: app.measurements_frame.canvas.yview_scroll(-2, "units"))
        self.edit_menu.add_command(
            label="Scroll Measurements Down",
            command=lambda: app.measurements_frame.canvas.yview_scroll(
                2, "units"),
            accelerator="{0}-Down".format(modifier))
        self.master.bind(
            "<{0}-Down>".format(modifier),
            lambda x: app.measurements_frame.canvas.yview_scroll(2, "units"))
        self.help_menu = Menu(self.menubar)
        self.menubar.add_cascade(menu=self.help_menu, label="Help")
        self.help_menu.add_command(
            label="Scan Session Tool Help",
            command=lambda: HelpDialogue(self.master), accelerator="F1")
        self.master.bind("<F1>", lambda x: HelpDialogue(self.master))
        self.master["menu"] = self.menubar


        self.master.resizable(False, False)
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid(sticky="WENS")
        self.general = ("Project:",
                        "Subject:",
                        #"Group:",
                        "Session:",
                        "Date:",
                        "Time A:",
                        "Time B:",
                        "User 1:",
                        "User 2:")
        self.documents = ["MR Safety Screening Form",
                          "Participation Informed Consent Form"]

        self.measurement = ("No.", "Type", "Vols", "Name",
                            "Logfiles", "Comments")

        self.documents_vars = []
        self.additional_documents = []
        self.additional_documents_vars = []
        self.additional_documents_widgets = []
        self.measurements = []
        self.measurements_widgets = []
        self.nofocus_widgets = []
        self.prt_files = []
        self.config = {}
        self.load_config()
        self.create_widgets()

        self.set_title()
        if platform.system() == "Darwin":
            self.master.bind('<Command-q>', self.quit_callback)
        self.master.bind('<Escape>', lambda x: self.master.focus())
        self.bind('<Button-1>', lambda x: self.master.focus())
        for label in self.nofocus_widgets:
            label.bind('<Button-1>', lambda x: self.master.focus())
        self.master.protocol("WM_DELETE_WINDOW", self.quit_callback)
        self.master.update()
        self.master.deiconify()
        self.master.lift()
        self.master.focus_force()
        self.general_widgets[0].focus()
        self.disable_save()
        self.mouseover_callback(True)

        if self.run_actions is not None:
            for key in run_actions:
                eval(f"self.{key}()")

    def create_widgets(self):
        self.top_frame = Frame(self)
        self.top_frame.columnconfigure(1, weight=1)
        self.top_frame.grid(row=0, sticky="WE", padx=10, pady=10)
        self.nofocus_widgets.append(self.top_frame)
        general_label = Label(self.top_frame, text="General Information")
        general_label['font'] = (self.default_font,
                                 self.default_font_size - 2,
                                 "bold")
        self.nofocus_widgets.append(general_label)
        self.general_frame = LabelFrame(self.top_frame,
                                        text='General Information',
                                        labelwidget=general_label,
                                        width=1024)
        self.general_frame.grid_columnconfigure(1, weight=1)
        self.general_frame.grid(row=0, column=0, sticky="NSWE")
        self.nofocus_widgets.append(self.general_frame)
        self.general_labels = []
        self.general_widgets = []
        self.general_vars = []


        self.general_frame_left = Frame(self.general_frame)
        self.general_frame_left.grid(row=0, column=0, sticky="N", padx=10)
        self.general_frame_right = Frame(self.general_frame)
        self.general_frame_right.grid(row=0, column=1, padx=10, sticky="N")

        for row, x in enumerate(self.general):
            label = Label(self.general_frame_left, text=x)
            label['font'] = (self.default_font, self.default_font_size, "bold")
            label.grid(row=row, column=0, sticky="E", padx=(0, 3), pady=3)
            self.general_labels.append(label)
            if row in (1, 2):
                width = 13  #10
                if platform.system() == "Windows":
                    width += 3
                frame = Frame(self.general_frame_left)  #, width=width) 
                var1 = StringVar()
                var1.trace("w", self.change_callback)
                var1.set("001")
                spinbox = Spinbox(frame, from_=1, to=999, format="%03.0f",
                                  width=3, justify="right", textvariable=var1,
                                  state="readonly", font=self.font,
                                  style="Orange.TSpinbox")
                spinbox.bind('<MouseWheel>', lambda x: 'break')
                pad = 7
                if platform.system() in ("Windows", "Linux"):
                    pad -= 4
                spinbox.grid(row=0, column=0, sticky="W", padx=(0,pad))
                var2 = StringVar()
                var2.trace("w", self.change_callback)
                combobox = AutocompleteCombobox(frame, textvariable=var2,
                                                validate=validate,
                                                validatecommand=vcmd,
                                                font=self.font, width=width)

                combobox.bind('<MouseWheel>', lambda x: 'break')
                combobox.grid(row=0, column=1, sticky="W")
                self.general_vars.append([var1, var2])
                self.general_widgets.append([spinbox, combobox])
                frame.grid(row=row, column=1, sticky="W")
            elif row in (0, 6, 7):
                var = StringVar()
                var.trace("w", self.change_callback)
                self.general_vars.append(var)
                validate = None
                vcmd = None
                if row == 0:
                    width = 20
                    if platform.system() == "Windows":
                        width += 3
                    combobox = AutocompleteCombobox(self.general_frame_left,
                                                    textvariable=var,
                                                    validate=validate,
                                                    validatecommand=vcmd,
                                                    font=self.font,
                                                    width=width,
                                                    style="Red.TCombobox")

                    combobox.bind('<MouseWheel>', lambda x: 'break')
                else:
                    width = 20
                    if platform.system() == "Windows":
                        width += 3
                    combobox = AutocompleteCombobox(
                        self.general_frame_left, textvariable=var,
                        validate=validate, validatecommand=vcmd,
                        font=self.font, width=width)

                if row == 0:
                    projects = sorted(self.config.keys())
                    combobox.set_completion_list(projects)
                combobox.grid(row=row, column=1, sticky="W")
                self.general_widgets.append(combobox)
            elif row in (3, 4, 5):
                var = StringVar()
                var.trace("w", self.change_callback)
                self.general_vars.append(var)
                if row == 3:
                    validate = "key"
                    vcmd = (self.master.register(self.validate),
                            "0123456789-", 10, '%S', '%P')
                    width = 10
                    self.autofill_date_callback()
                elif row in (4, 5):
                    validate = "key"
                    vcmd = (self.master.register(self.validate),
                            "0123456789:-", 11, '%S', '%P')
                    width = 10
                if row == 3:
                    entry = Entry(self.general_frame_left, width=width,
                                  textvariable=var, validate=validate,
                                  validatecommand=vcmd, font=self.font,
                                  style="Orange.TEntry")
                else:
                    entry = Entry(self.general_frame_left, width=width,
                                  textvariable=var, validate=validate,
                                  validatecommand=vcmd, font=self.font)
                entry.grid(row=row, column=1, sticky="W")
                self.general_widgets.append(entry)

        notes_label = Label(self.general_frame_right, text="Notes:",
                            style="Green.TLabel")
        notes_label.grid(row=0, column=0, sticky="W")
        notes_label['font'] = (self.default_font, self.default_font_size,
                               "bold")
        notes_container = FixedSizeFrame(self.general_frame_right, 299, 171)
        notes_container.grid(row=1, column=0, sticky="N")
        notes = AutoScrollbarText(notes_container, wrap=NONE)
        notes.grid(row=0, column=0, sticky="N")
        self.general_widgets.append(notes)
        notes.bind('<KeyRelease>', self.change_callback)

        for label in self.general_labels:
            self.nofocus_widgets.append(label)

        self.control_frame = Frame(self.top_frame)
        self.control_frame.grid_rowconfigure(0, weight=1)
        self.control_frame.grid(row=0, column=1, sticky="NS")
        self.nofocus_widgets.append(self.control_frame)
        self.logo = Frame(self.control_frame)
        self.logo.grid(row=0, column=0)
        self.nofocus_widgets.append(self.logo)
        self.title1 = Label(self.logo, text="Scan",
                           justify="center", style="Blue.TLabel")
        self.title1.grid(row=0)
        self.title1['font'] = (self.default_font,
                              self.default_font_size - 10,
                              "bold")
        self.nofocus_widgets.append(self.title1)
        self.title2 = Label(self.logo, text="Session",
                           justify="center", style="Blue.TLabel")
        self.title2.grid(row=1)
        self.title2['font'] = (self.default_font,
                              self.default_font_size - 10,
                              "bold")
        self.nofocus_widgets.append(self.title2)
        self.title3 = Label(self.logo, text="Tool",
                           justify="center", style="Blue.TLabel")
        self.title3.grid(row=2)
        self.title3['font'] = (self.default_font,
                              self.default_font_size - 10,
                              "bold")
        self.nofocus_widgets.append(self.title3)
        self.version1 = Label(self.logo,
                             text="Version {0}".format(__version__),
                             style="Blue.TLabel")
        self.version1.grid(row=3)
        self.version1['font'] = (self.default_font, self.default_font_size + 2)
        self.nofocus_widgets.append(self.version1)
        self.version2 = Label(self.logo,
                             text="({0})".format(__date__),
                             style="Blue.TLabel")
        self.version2.grid(row=4)
        self.version2['font'] = (self.default_font, self.default_font_size + 2)
        self.nofocus_widgets.append(self.version2)
        self.help = Button(self.logo, text="?", width=1,
                           command=lambda: HelpDialogue(self.master))
        self.help.grid(row=5, pady=5)

        self.button_frame = Frame(self.control_frame)
        self.button_frame.grid(row=1, column=0, padx=10)
        self.nofocus_widgets.append(self.button_frame)
        self.open_button = Button(self.button_frame, text="Open",
                                  command=self.open, state="enabled")
        self.open_button.grid(row=0, column=0, sticky="")
        self.save_button = Button(self.button_frame, text="Save",
                                  command=self.save)
        self.save_button.grid(row=1, column=0, sticky="", pady=3)
        self.go_button = Button(self.button_frame, text="Archive",
                                state="disabled", command=self.archive)
        self.go_button.grid(row=2, column=0, sticky="")
        documents_label = Label(self.top_frame, text="Documents")
        documents_label['font'] = (self.default_font,
                                   self.default_font_size - 2,
                                   "bold")
        self.nofocus_widgets.append(documents_label)
        self.documents_frame = LabelFrame(self.top_frame, text='Documents',
                                          labelwidget=documents_label)
        self.documents_frame.grid(row=0, column=2, sticky="NSE")
        self.nofocus_widgets.append(self.documents_frame)
        files_label = Label(self.documents_frame, text="Files:")
        files_label.grid(row=0, sticky="W", padx=10)
        files_label['font'] = (self.default_font, self.default_font_size,
                               "bold")

        self.nofocus_widgets.append(files_label)
        files_container = FixedSizeFrame(self.documents_frame, 299, 53)  #68
        files_container.grid(row=1, sticky="NSEW", padx=10)
        self.nofocus_widgets.append(files_container)
        self.files = AutoScrollbarText(files_container, wrap=NONE,
                                       background=self.orange,
                                       highlightbackground=self.orange)
        self.files.bind('<KeyRelease>', self.change_callback)
        self.files.grid(sticky="NWES")
        empty_label = Label(self.documents_frame, text="")
        empty_label.grid(row=2, sticky="W", padx=10)
        self.nofocus_widgets.append(empty_label)
        checklist_label = Label(self.documents_frame, text="Checklist:")
        checklist_label.grid(row=3, sticky="W", padx=10)
        checklist_label['font'] = (self.default_font, self.default_font_size,
                                   "bold")
        self.nofocus_widgets.append(checklist_label)
        self.documents_labels = []
        self.documents_checks = []
        self.documents_vars = []
        for row, x in enumerate(self.documents):
            var = IntVar()
            var.trace("w", self.change_callback)
            check = Checkbutton(self.documents_frame, text=x, variable=var)
            check.grid(row=row+4, sticky="W", padx=10)
            self.documents_vars.append(var)

        self.bottom_frame = Frame(self)
        self.bottom_frame.grid_columnconfigure(0, weight=1)
        self.bottom_frame.grid(row=1, column=0, padx=10, pady=10,
                               sticky="WENS")
        self.nofocus_widgets.append(self.bottom_frame)
        measurements_label = Label(self.bottom_frame, text="Measurements")
        measurements_label['font'] = (self.default_font,
                                      self.default_font_size - 2,
                                      "bold")
        self.nofocus_widgets.append(measurements_label)
        self.measurements_frame1 = LabelFrame(self.bottom_frame,
                                              text='Measurements',
                                              labelwidget=measurements_label)
        self.measurements_frame1.grid_rowconfigure(1, weight=1)
        self.measurements_frame1.grid(row=0, sticky="WENS")
        self.nofocus_widgets.append(self.measurements_frame1)
        self.measurements_frame = VerticalScrolledFrame(
            self.measurements_frame1, height=295, width=989) #989
        self.measurements_frame.interior.grid_columnconfigure(0, weight=1)
        self.measurements_frame.interior.grid_rowconfigure(0, weight=1)
        self.measurements_frame.grid(row=1, sticky="WENS")
        self.nofocus_widgets.append(self.measurements_frame)
        self.nofocus_widgets.append(self.measurements_frame.interior)
        self.nofocus_widgets.append(self.measurements_frame.canvas)
        add_del_frame = Frame(self.measurements_frame1)
        add_del_frame.grid(row=2, pady=(10, 10))
        self.scanning_add = Button(add_del_frame,
                                   text="+", width=3,
                                   command=self.new_measurement)
        self.scanning_add.grid(row=0, column=0, padx=5)
        self.scanning_del = Button(add_del_frame,
                                   text="-", width=3,
                                   command=self.del_measurement)
        self.scanning_del.grid(row=0, column=1, padx=5)
        self.measurements_frame.canvas.bind("<Double-Button-1>",
                                            lambda x: self.new_measurement())

        label_frame = Frame(self.measurements_frame1)
        label_frame.grid(row=0, columnspan=6, sticky="W")
        for column, x in enumerate(self.measurement):
            label = Label(label_frame, text=x)
            if column == 0:
                p = 18
                if platform.system() in ("Windows", "Linux"):
                    p -= 2
                label.grid(row=0, column=column, padx=(p, 0), pady=(3, 3))
            elif column == 1:
                p = 43
                if platform.system() == "Windows":
                    p += 2
                if platform.system() == "Linux":
                    p += 12
                label.grid(row=0, column=column, padx=(p, 0))
            elif column == 2:
                p = 41
                if platform.system() == "Windows":
                    p += 1
                if platform.system() == "Linux":
                    p += 13
                label.grid(row=0, column=column, padx=(p, 0))
            elif column == 3:
                p = 69
                if platform.system() == "Windows":
                    p -= 1
                if platform.system() == "Linux":
                    p -= 12
                label.grid(row=0, column=column, padx=(p, 0))
            elif column == 4:
                p = 201
                if platform.system() == "Windows":
                    p += 2
                if platform.system() == "Linux":
                    p -= 5
                label.grid(row=0, column=column, padx=(p, 0))
            elif column == 5:
                p = 239
                if platform.system() == "Windows":
                    p += 4
                label.grid(row=0, column=column, padx=(p, 130))

            label['font'] = (self.default_font, self.default_font_size,
                             "bold")
            label.bind('<Button-1>', lambda x: app.master.focus())
        self.new_measurement()


    def new_measurement(self, *args):
        value = repr(len(self.measurements) + 1).zfill(3)
        scanning_vars = []
        scanning_widgets = []
        var1 = StringVar()
        scanning_vars.append(var1)
        var1.set(value)
        var1.trace("w", self.change_callback)
        spinbox = Spinbox(self.measurements_frame.interior, from_=1, to=99,
                          format="%03.0f",width=3, justify="right",
                          state="readonly", textvariable=var1, font=self.font,
                          style="Orange.TSpinbox")

        spinbox.grid(row=int(value), column=0, sticky="W", padx=(10, 2))
        spinbox.bind('<Enter>',
                     lambda event: self.mouseover_callback(True))
        spinbox.bind('<Leave>',
                     lambda event: self.mouseover_callback(False))
        spinbox.bind('<MouseWheel>', lambda x: 'break')
        scanning_widgets.append(spinbox)
        var2 = StringVar()
        var2.trace("w", self.change_callback)
        scanning_vars.append(var2)

        width = 9
        if platform.system() == "Windows":
            width += 2
        if platform.system() == "Linux":
            width += 5
        combobox = AutocompleteCombobox(self.measurements_frame.interior,
                            textvariable=var2, width=width, state="readonly",
                            font=self.font, style="Orange.TCombobox")
        combobox.set_completion_list(["anat", "func", "misc"])
        combobox.current(0)
        combobox.grid(row=int(value), column=1, sticky="", padx=2)
        combobox.bind('<Enter>',
                      lambda event: self.mouseover_callback(True))
        combobox.bind('<Leave>',
                      lambda event: self.mouseover_callback(False))
        combobox.bind('<MouseWheel>', lambda x: 'break')
        scanning_widgets.append(combobox)

        var3 = StringVar()
        var3.trace("w", self.change_callback)
        scanning_vars.append(var3)
        validate = "key"
        vcmd = (self.master.register(self.validate),
                "0123456789", 4, '%S', '%P')

        vols = Entry(self.measurements_frame.interior, width=4,
                       justify="right", textvariable=var3,
                       validate=validate, validatecommand=vcmd,
                       font=self.font, style="Red.TEntry")
        vols.bind('<MouseWheel>', lambda x: 'break')
        vols.grid(row=int(value), column=2, sticky="", padx=2)
        scanning_widgets.append(vols)
        var4 = StringVar()
        var4.trace("w", self.change_callback)
        scanning_vars.append(var4)
        validate = None
        vcmd = None
        width = 20
        if platform.system() == "Windows":
            width += 3
        name = AutocompleteCombobox(self.measurements_frame.interior,
                                    textvariable=var4, validate=validate,
                                    validatecommand=vcmd, font=self.font,
                                    style="Red.TCombobox", width=width)
        name.grid(row=int(value), column=3, sticky="", padx=2)
        name.bind('<Enter>',
                  lambda event: self.mouseover_callback(True))
        name.bind('<Leave>',
                        lambda event: self.mouseover_callback(False))
        name.bind('<MouseWheel>', lambda x: 'break')
        scanning_widgets.append(name)
        container2 = FixedSizeFrame(self.measurements_frame.interior, 299, 53)
        container2.grid(row=int(value), column=4, sticky="NSE", pady=3, padx=2)
        scanning_widgets.append(container2)
        logfiles = AutoScrollbarText(container2, wrap=NONE,
                                     background=self.orange,
                                     highlightbackground=self.orange)
        logfiles.bind('<KeyRelease>', self.change_callback)
        logfiles.frame.bind('<Enter>',
                        lambda event: self.mouseover_callback(True))
        logfiles.frame.bind('<Leave>',
                        lambda event: self.mouseover_callback(False))
        scanning_vars.append(logfiles)  # Needs to be called with START, END!
        logfiles.grid()
        scanning_widgets.append(logfiles)
        container3 = FixedSizeFrame(self.measurements_frame.interior, 299, 53)
        container3.grid(row=int(value), column=5, sticky="NSE", pady=3,
                        padx=(2, 10))
        scanning_widgets.append(container3)
        text = AutoScrollbarText(container3, wrap=NONE)
        text.bind('<KeyRelease>', self.change_callback)
        text.frame.bind('<Enter>',
                        lambda event: self.mouseover_callback(True))
        text.frame.bind('<Leave>',
                        lambda event: self.mouseover_callback(False))
        scanning_vars.append(text)  # Needs to be called with START, END!
        text.grid()
        scanning_widgets.append(text)
        self.measurements.append(scanning_vars)
        self.measurements_widgets.append(scanning_widgets)
        self.change_callback(str(var2))  # Update Names
        self.prt_files.append("")

    def del_measurement(self, *args):
        for s in self.measurements_widgets[-1]:
            s.grid_remove()
            del s
        self.measurements_widgets.pop()
        self.measurements.pop()
        self.change_callback(None)

    def add_additional_documents(self):
        current_project = self.general_widgets[0].get()
        try:
            for x in self.config[current_project]["Checklist"]:
                if not x in self.documents:
                    var = IntVar()
                    var.trace("w", self.change_callback)
                    check = Checkbutton(self.documents_frame, text=x,
                                        variable=var)
                    check.grid(sticky="W", padx=10)
                    self.documents.append(x)
                    self.documents_vars.append(var)
                    self.additional_documents.append(x)
                    self.additional_documents_vars.append(var)
                    self.additional_documents_widgets.append(check)
        except:
            pass

    def add_files(self):
        current_project = self.general_widgets[0].get()
        try:
            for x in self.config[current_project]["Files"]:
                if not x in self.files.get(1.0, END).strip("\n"):
                    self.files.insert(END, x + '\n')
        except:
            pass

    def del_additional_documents(self):
        self.general_widgets[1][1].set_completion_list([])
        self.general_widgets[2][1].set_completion_list([])
        self.general_widgets[6].set_completion_list([])
        self.general_widgets[7].set_completion_list([])
        self.files.delete(1.0, END)
        for index, m in enumerate(self.measurements_widgets):
            t = self.measurements[index][1].get()
            m[3].set_completion_list([])
        for w in self.additional_documents_widgets:
            w.grid_remove()
        for v in self.additional_documents_vars:
            try:
                self.documents_vars.remove(v)
            except:
                pass
        for x in self.additional_documents:
            try:
                self.documents.remove(x)
            except:
                pass
        self.additional_documents_vars = []
        self.additional_documents_widgets = []

    def autofill_date_callback(self, *args):
        date = time.strftime("%Y-%m-%d", time.localtime())
        self.general_vars[3].set(date)

    def mouseover_callback(self, mouseover):
        if len(self.measurements) >= 6:
            if mouseover:
                self.measurements_frame.unbind_mouse_wheel()
            else:
                self.measurements_frame.bind_mouse_wheel()

    def validate(self, allowed_chars, allowed_length, current_char,
                 resulting_string):
        if current_char in allowed_chars:
            if len(resulting_string) <= int(allowed_length):
                return True
            else:
                return False
        else:
            return False

    def enable_save(self):
        self.save_button["state"] = "enabled"
        self.file_menu.entryconfigure("Save", state="normal")
        if platform.system() == "Darwin":
            self.master.bind("<Command-s>", self.save)
        else:
            self.master.bind("<Control-s>", self.save)

    def disable_save(self):
        self.save_button["state"] = "disabled"
        self.file_menu.entryconfigure("Save", state="disabled")
        if platform.system() == "Darwin":
            self.master.unbind("<Command-s>")
        else:
            self.master.unbind("<Control-s>")

    def enable_archive(self):
        self.go_button["state"] = "enabled"
        self.file_menu.entryconfigure("Archive", state="normal")
        if platform.system() == "Darwin":
            self.master.bind("<Command-r>", self.archive)
        else:
            self.master.bind("<Control-r>", self.archive)

    def disable_archive(self):
        self.go_button["state"] = "disabled"
        self.file_menu.entryconfigure("Archive", state="disabled")
        if platform.system() == "Darwin":
            self.master.unbind("<Command-r>")
        else:
            self.master.unbind("<Control-r>")

    def enable_minus(self):
        self.scanning_del["state"] = "enabled"
        self.edit_menu.entryconfigure("Delete Measurement", state="normal")
        if platform.system() == "Darwin":
            self.master.bind("<Command-d>", self.del_measurement)
        else:
            self.master.bind("<Control-d>", self.del_measurement)

    def disable_minus(self):
        self.scanning_del["state"] = "disabled"
        self.edit_menu.entryconfigure("Delete Measurement", state="disabled")
        if platform.system() == "Darwin":
            self.master.unbind("<Command-d>")
        else:
            self.master.unbind("<Control-d>")

    def quit_callback(self, *args):
        if self.save_button["state"] == "enabled":
            if tkMessageBox.askyesno("Save?", "Save before quitting?"):
                self.save()
        self.master.destroy()

    def change_callback(self, *args):
        try:
            self.enable_save()
        except:
            pass

        current_project = self.general_vars[0].get()

        # Update project
        if args[0] == str(self.general_vars[0]):
            self.del_additional_documents()
            try:
                if self.config[current_project]["SubjectTypes"] is not None:
                    self.general_widgets[1][1].set_completion_list(
                        self.config[current_project]["SubjectTypes"])
            except:
                pass
            try:
                if self.config[current_project]["SessionTypes"] is not None:
                    self.general_widgets[2][1].set_completion_list(
                        self.config[current_project]["SessionTypes"])
            except:
                pass
            try:
                if self.config[current_project]["Users"] is not None:
                    self.general_widgets[6].set_completion_list(
                        self.config[current_project]["Users"])
            except:
                pass
            try:
                if self.config[current_project]["Users"] is not None:
                    self.general_widgets[7].set_completion_list(
                        self.config[current_project]["Users"])
            except:
                pass
            for index, m in enumerate(self.measurements_widgets):
                try:
                    t = self.measurements[index][1].get()
                    m[3].set_completion_list(
                        [x["Name"] for x in self.config[current_project]["Measurements " + t]])
                except:
                    pass
            self.add_additional_documents()
            self.add_files()

            # Update notes
            if current_project != "":
                try:
                    notes = self.config[current_project]["Notes"]
                    if notes is not None:
                        self.general_widgets[-1].delete(1.0, END)
                        self.general_widgets[-1].insert(END, notes)
                except:
                    pass

        # Check if archving is possible
        try:
            if current_project != "" and \
                            self.general_vars[0].get() != "" and \
                            self.general_vars[3].get()!= "":
                self.enable_archive()
            else:
                self.disable_archive()
        except:
            pass

        # Check if deleting measurement is possible
        try:
            if len(self.measurements) > 1 and \
                self.measurements[-1][2].get() == "" and \
                self.measurements[-1][3].get() == "" and \
                self.measurements_widgets[-1][5].get(
                        1.0, END).strip("\n") == "" and \
                self.measurements_widgets[-1][-1].get(
                        1.0, END).strip("\n") == "":
                self.enable_minus()
            else:
                self.disable_minus()
        except:
            pass

        # Adapt Measurement Names according to Type
        types = [str(x[1]) for x in self.measurements]
        try:
            idx = types.index(args[0])
        except:
            idx = None
        if idx is not None and current_project != "":
            try:
                t = self.measurements[idx][1].get()
                self.measurements_widgets[idx][3].set_completion_list(
                    [x["Name"] for x in self.config[current_project]["Measurements " + t]])
            except:
                pass

        # Adapt Vols, Protocol and Comments according to Measurement Name
        names = [str(x[3]) for x in self.measurements]
        try:
            idx = names.index(args[0])
        except:
            idx = None
        if idx is not None and current_project != "":
            try:
                t = self.measurements[idx][1].get()
                n = self.measurements[idx][3].get()
                if n != "":
                    try:
                        id = [name for name in self.config[current_project]["Measurements " + t] if name["Name"] == n]
                        try:
                            vols = id[0]["Vols"]
                            if vols is not None:
                                self.measurements[idx][2].set(vols)
                        except:
                            pass
                        try:
                            comments = id[0]["Comments"]
                            if comments is not None:
                                self.measurements_widgets[idx][-1].delete(1.0,
                                                                          END)
                                self.measurements_widgets[idx][-1].insert(
                                    END, comments)
                        except:
                            pass
                    except:
                        pass
                    if t != "anat":
                        e = "*"

                        prt = "_".join(self.get_filename().split("_")[1:4]) + \
                            "_" + n + "." + e
                        if prt != self.prt_files[idx]:
                            if self.prt_files[idx] == "":
                                start = 1.0
                            elif self.prt_files[idx] != "":
                                start = self.measurements[idx][4].search(
                                    self.prt_files[idx], 1.0, stopindex=END)
                                end = ".".join([start.split(".")[0],
                                            repr(len(self.prt_files[idx]))])
                                self.measurements[idx][4].delete(start, end)
                            self.measurements[idx][4].insert(start, prt)
                            self.prt_files[idx] = prt

            except:
                pass

    def load_config(self):
        """Load the config file."""

        path = None
        if os.path.exists("sst.yaml"):
            path = os.path.curdir
        elif os.path.exists(os.path.join(os.path.expanduser("~"), "sst.yaml")):
            path = os.path.expanduser("~")
        else:
            if os.path.isfile(os.path.join(os.path.split(__file__)[0], "sst.yaml")):
                path = os.path.split(__file__)[0]
        if path is not None:
            with open(os.path.join(path, "sst.yaml")) as f:
                self.config = yaml.safe_load(f)

    def get_filename(self):
        proj = self.general_vars[0].get()
        if proj == "":
            proj = "Project"
        subj_nr = self.general_vars[1][0].get()
        subj = "sub-" + repr(int(subj_nr)).zfill(3)
        subj_type = self.general_vars[1][1].get()
        if subj_type != "":
            subj = "{0}-{1}".format(subj, subj_type)
        ses_nr = self.general_vars[2][0].get()
        ses = "ses-" + repr(int(ses_nr)).zfill(3)
        ses_type = self.general_vars[2][1].get()
        if ses_type != "":
            ses = "{0}-{1}".format(ses, ses_type)
        date = self.general_vars[3].get()
        if date == "":
            date = "Date"
        else:
            date = "".join(date.split("-"))
        filename = "ScanProtocol_{0}_{1}_{2}_{3}".format(proj, subj, ses,
                                                         date)
        return filename

    def save(self, filename=None, *args):
        """Save a protocol file."""

        if self.run_actions is not None and "save" in self.run_actions:
            f = open(self.run_actions["save"][0], 'w')
        else:
            if filename is None:
                filename = self.get_filename()
                f = tkFileDialog.asksaveasfile(mode='w',
                                               defaultextension='.txt',
                                               initialfile=filename)
            else:
                f = open(filename, 'w')

        if f is None:
            return

        f.write("General Information\n")
        f.write("===================\n")
        f.write("\n")
        for pos, label in enumerate(self.general):
            if pos in (1,2):
                try:
                    value1 = self.general_vars[pos][0].get().zfill(3)
                    value2 = " " + self.general_vars[pos][1].get()
                    if pos == 1:
                        value2 = value2.lstrip(" ")
                except:
                    value1 = "000"
                    value2 = ""
                f.write("{0}{1}{2}\n".format(label, " "*(24-len(label)),
                                             value1 + value2))
            else:
                try:
                    value = self.general_vars[pos].get()
                except:
                    value = ""
                if value == "":
                    f.write("{0}\n".format(label))
                else:
                    f.write("{0}{1}{2}\n".format(label, " "*(24-len(label)),
                                                 value))

        f.write("\nNotes:")
        notes = self.general_widgets[-1].get(1.0, END)
        if notes.strip() != "":
            notes_lines = [x.strip() for x in notes.split("\n")]
            try:
                for line_nr, line in enumerate(notes_lines[:-1]):
                    if line_nr == 0:
                        f.write("{0}{1}".format(" "*(24-len("Notes:")), line))
                    else:
                        f.write("\n{0}{1}".format(" "*24, line))
            except:
                pass
        f.write("\n")
        f.write("\n")
        f.write("\n")
        f.write("Documents\n")
        f.write("=========\n")

        f.write("\nFiles:")
        files = self.files.get(1.0, END).split("\n")
        file_lines = [x.strip() for x in files if x != ""]
        try:
            for line_nr, line in enumerate(file_lines):
                if line_nr == 0:
                    f.write("{0}{1}".format(" "*(24-len("Files:")), line))
                else:
                    f.write("\n{0}{1}".format(" "*24, line))
        except:
            pass

        f.write("\n\nChecklist:")
        states = ("[ ]", "[x]")
        for pos, label in enumerate(self.documents):
            try:
                value = int(self.documents_vars[pos].get())
            except:
                value = 0
            if pos == 0:
                f.write("{0}{1} {2}".format(" "*(24-len("Checklist:")),
                                            states[value], label))
            else:
                f.write("\n{0}{1} {2}".format(" "*24, states[value], label))

        f.write("\n")
        f.write("\n")
        f.write("\n")
        f.write("Measurements\n")
        f.write("============")
        f.write("\n")
        for m in self.measurements:
            f.write("\nNo. {0}\n".format(int(m[0].get())))
            f.write("-----\n\n")
            for elem in range(1, len(self.measurement)-1):
                if elem == 4:
                    try:
                        logfiles = m[elem].get(1.0, END).split("\n")
                        logfile_lines = [x.strip() for x in logfiles if x != ""]
                        l = [" "*24 + x if index > 0 \
                                 else x for index, x in enumerate(logfile_lines)]
                        value = "\n".join(l)
                    except:
                        value = ""
                else:
                    try:
                        value = m[elem].get()
                    except:
                        value = ""
                if value == "":
                    f.write("{0}:\n".format(self.measurement[elem]))
                else:
                    f.write("{0}:{1}{2}\n".format(
                        self.measurement[elem],
                        " "*(23-len(self.measurement[elem])),
                        value))

            f.write("\nComments:")

            comments = m[-1].get(1.0, END)
            if comments.strip("\n") != "":
                comment_lines = [x.strip() for x in comments.split("\n")]
                try:
                    for line_nr, line in enumerate(comment_lines[:-1]):
                        if line_nr == 0:
                            f.write("{0}{1}".format(" "*(24-len("Comments:")),
                                                    line))
                        else:
                            f.write("\n{0}{1}".format(" "*24, line))
                except:
                    pass
            f.write("\n\n")
        f.close()
        self.disable_save()

    def open(self, *args):
        """Open a protocol file."""

        if self.run_actions is not None and "open" in self.run_actions:
            f = open(self.run_actions["open"][0])
        else:
            f = tkFileDialog.askopenfile("r", filetypes=[("text files", ".txt")])
        if f is not None:
            current_document = 0
            measurement = False
            measurement_starts = []
            notes_block = False
            comments_block = False
            files_block = False
            if len(self.measurements) == 0:
                self.new_measurement()
            while len(self.measurements) > 1:
                self.del_measurement()
            for m in self.measurements:
                m[-1].delete(1.0, END)
            for linenr, line in enumerate(f):
                if 3 <= linenr <= 10:
                    if linenr in (4,5):
                        self.general_vars[linenr-3][0].set((line[24:27]))
                        self.general_vars[linenr-3][1].set(line[28:].strip())
                    else:
                        self.general_vars[linenr-3].set(line[24:].strip())
                    if linenr == 3:
                        self.del_additional_documents()
                elif not measurement:
                    if line.startswith("Notes:"):
                        notes_block = True
                        self.general_widgets[-1].delete(1.0, END)
                    if line.startswith("Files:"):
                        files_block = True
                        self.files.delete(1.0, END)
                    if line.startswith("Checklist:"):
                        files_block = False
                    if notes_block:
                        if line.startswith("Documents"):
                            notes_block = False
                        else:
                            if self.general_widgets[-1].get(
                                1.0, END).strip("\n") == "":
                                self.general_widgets[-1].insert(
                                    END, line[24:].strip())
                            elif line != "\n":
                                self.general_widgets[-1].insert(
                                    END, "\n" + line[24:].strip())
                    elif files_block:
                        if self.files.get(1.0, END).strip("\n") == "":
                            self.files.insert(END, line[24:].strip())
                        else:
                            self.files.insert(END, "\n" + line[24:].strip())
                    elif line.startswith("Measurements"):
                        measurement = True
                    else:
                        try:
                            check = line[25]
                            if check == " ":
                                value = 0
                            elif check == "x":
                                value = 1

                            x = line[27:].strip()
                            if line[24:].startswith("[") and not x in \
                                    self.documents:
                                var = IntVar()
                                var.trace("w", self.change_callback)
                                check = Checkbutton(self.documents_frame,
                                                    text=x, variable=var)
                                check.grid(sticky="W", padx=10)
                                self.documents.append(x)
                                self.documents_vars.append(var)
                                self.additional_documents.append(x)
                                self.additional_documents_vars.append(var)
                                self.additional_documents_widgets.append(check)

                            self.documents_vars[current_document].set(value)
                            current_document += 1
                        except:
                            pass

                elif measurement:
                    if line.startswith("===") or line.strip() == "":
                        pass
                    elif line.startswith("No. "):
                        if measurement_starts != []:
                            self.new_measurement()
                        self.measurements[len(measurement_starts)][0].set(
                            line[4:].strip().zfill(3))
                        measurement_starts.append(linenr)
                        comments_block = False
                    elif linenr >= measurement_starts[-1]+3:
                        if line.startswith("Type:") or\
                                line.startswith("Vols:") or\
                                line.startswith("Name:"):
                            self.measurements[
                                len(measurement_starts)-
                                1][linenr-measurement_starts[-1]-
                                   2].set(line[24:].strip())
                        elif line.startswith("Logfiles:"):
                            widget = self.measurements[
                                len(measurement_starts)-
                                1][-2]
                            widget.delete(1.0, END)
                            widget.insert(END, line[24:].strip())
                        elif line.startswith(" " * 24) and \
                            comments_block == False:
                            widget = self.measurements[
                                len(measurement_starts)-
                                1][-2]
                            widget.insert(END, "\n" + line[24:].strip())
                    if line.startswith("Comments:"):
                        if comments_block is False:
                            comments_block = True
                            self.measurements[len(measurement_starts)-
                                              1][-1].delete(1.0, END)

                    if comments_block:
                        if self.measurements[len(measurement_starts)-
                                1][-1].get( 1.0, END).strip("\n") == "":
                            self.measurements[len(measurement_starts)-
                                              1][-1].insert(END,
                                                            line[24:].strip())
                        elif line != "\n":
                            self.measurements[len(measurement_starts)-
                                              1][-1].insert(
                                                  END,
                                                  "\n" + line[24:].strip())

            self.disable_save()
        try:
            f.close()
        except:
            pass

    def set_title(self, status=None):
        if status is None:
            self.master.title('Scan Session Tool')
        else:
            self.master.title('Scan Session Tool ({0})'.format(status))

    def _archive_runs(self, archiving, dialogue):
        if self.run_actions is not None and "archive" in self.run_actions:
            run_as_action = True
        else:
            run_as_action = False

        d, folder, bv_links, tbv_links, tbv_files, tbv_prefix = archiving
        warnings = "\n\n\n"
        project = self.general_vars[0].get()
        subject_no = int(self.general_vars[1][0].get())
        subject_type = self.general_vars[1][1].get()
        session_no = int(self.general_vars[2][0].get())
        session_type = self.general_vars[2][1].get()

        project_folder = os.path.join(folder, project)
        if subject_type == "":
            subject_folder = os.path.join(project_folder,
                                          "sub-" + repr(
                                              subject_no).zfill(3))
        else:
            subject_folder = os.path.join(
                project_folder, "sub-" + repr(
                    subject_no).zfill(3) + "-" + subject_type)

        if session_type == "":
            session_folder = os.path.join(
                subject_folder, "ses-" + repr(session_no).zfill(3))
        else:
            session_folder = os.path.join(
                subject_folder,
                "ses-" + repr(session_no).zfill(3) + "-" + session_type)

        if os.path.exists(session_folder):
            self.message = \
                "Archiving failed: {0} already exists!".format(session_folder)
            return
        else:
            try:
                os.makedirs(session_folder)
            except:
                self.message = \
                    "Archiving failed: Could not create target directory!"
                return

        dialogue.update(status=["Preparation", "Reading DICOM images..."])
        if run_as_action:
            while self.master.tk.dooneevent(_tkinter.DONT_WAIT):
                pass

        all_dicoms = []
        for root, _, files in os.walk(d):
            for f in files:
                if os.path.splitext(f)[-1] in (".dcm", ".IMA"):
                    all_dicoms.append(os.path.join(root, f))

        pool = multiprocessing.Pool()
        imap = pool.imap_unordered

        scans = {}  # scans[RUN][VOLUME][ECHO]["protocolname"|"acquisition_nr"|"filename"]
        for counter, dicom in enumerate(imap(readdicom, all_dicoms)):
            percentage = int(
                round((float(counter) + 1) / len(all_dicoms) * 100))
            dialogue.update(
                status=["Preparation",
                        "Reading DICOM images...{0}%".format(percentage)])
            if run_as_action:
                self.master.tk.dooneevent(_tkinter.DONT_WAIT)

            try:
                scans[dicom[1]]
            except KeyError:
                scans[dicom[1]] = {}

            try:
                scans[dicom[1]][dicom[3]]
            except KeyError:
                scans[dicom[1]][dicom[3]] = {}

            scans[dicom[1]][dicom[3]][dicom[5]] = \
                {"protocolname": dicom[4],
                    "acquisition_nr": dicom[2],
                    "filename": dicom[0]}
        pool.close()

        for meas_counter, measurement in enumerate(self.measurements):
            number = int(measurement[0].get())
            type = measurement[1].get()
            try:
                vols = int(measurement[2].get())
            except:
                vols = 0
            name = measurement[3].get()

            if name == "":
                warnings += "\nError copying images for measurement {0}:\n" \
                           "    'Name' not specified\n".format(number)
            elif vols == 0:
                warnings += "\nError copying images for measurement {0}:\n" \
                           "    'Vols' not specified\n".format(number)
            elif scans == {}:
                warnings += "\nError copying images for measurement {0}:\n" \
                            "    No images found\n".format(number)
#            elif len(scans[number]) != vols:
#                warnings += "\nError copying images for measurement {0}:" \
#                            "    'Vols' unequals number of images\n".format(
#                                number)
            else:
                try:
                    type_folder = os.path.join(session_folder, type)
                    if not os.path.exists(type_folder):
                        os.makedirs(type_folder)
                    name_folder = os.path.join(
                        type_folder, repr(number).zfill(3) + "-" + name)
                    if not os.path.exists(name_folder):
                        os.makedirs(name_folder)
                except:
                    warnings += "\nError creating directory structure for " \
                                "measurement {0}\n".format(number)
                    shutil.rmtree(dicom_folder)

                # DICOMs
                dialogue.update(status=["Measurement {0} ({1} of {2})".format(
                    number, meas_counter+1, len(self.measurements)),
                                        "Copying DICOM files..."])
                if run_as_action:
                    while self.master.tk.dooneevent(_tkinter.DONT_WAIT):
                        pass

                try:
                    dicom_folder = os.path.join(name_folder, "DICOM")
                    if not os.path.exists(dicom_folder):
                        os.makedirs(dicom_folder)

                    for counter, image in enumerate(scans[number]):
                        for echo in scans[number][image]:
                            percentage = int(round(
                                (float(counter) + 1) / len(scans[number]) * 100))
                            dialogue.update(
                                status=["Measurement {0} ({1} of {2})".format(
                                    number, meas_counter + 1,
                                    len(self.measurements)),
                                        "Copying DICOM files...{0}%".format(
                                            percentage)])
                            if run_as_action:
                                self.master.tk.dooneevent(_tkinter.DONT_WAIT)

                            shutil.copyfile(
                                scans[number][image][echo]["filename"],
                                os.path.join(dicom_folder, os.path.split(
                                    scans[number][image][echo]["filename"])[-1]))
                except:
                    warnings += "\nError copying images for measurement " \
                                "{0}:\n    Filesystem error\n".format(number)
                    shutil.rmtree(dicom_folder)

                # BV Files                       
                if bv_links == True:
                    dialogue.update(
                        status=["Measurement {0} ({1} of {2})".format(
                            number, meas_counter+1, len(self.measurements)),
                                "Creating BrainVoyager links..."])
                    if run_as_action:
                        while self.master.tk.dooneevent(_tkinter.DONT_WAIT):
                            pass

                    try:
                        bv_folder = os.path.join(session_folder, "BV")
                        if not os.path.exists(bv_folder):
                            os.makedirs(bv_folder)

                        for counter, image in enumerate(scans[number]):
                            for echo in scans[number][image]:
                                percentage = int(round((float(counter) + 1) / len(
                                    scans[number]) * 100))
                                dialogue.update(
                                    status=["Measurement {0} ({1} of {2})".format(
                                        number, meas_counter + 1,
                                        len(self.measurements)),
                                            "Creating BrainVoyager links...{0}%".format(
                                                percentage)])
                                if run_as_action:
                                    self.master.tk.dooneevent(_tkinter.DONT_WAIT)

                                prefix = "{}_{:03d}{}".format(
                                    "_".join(self.get_filename().split(
                                        "_")[1:-1]).replace("-", ""),
                                    number, name)
                                if len(scans[number][image]) > 1:
                                    prefix += "_{}".format(echo)
                                target_name = "{}-{:04d}-{:04d}-{:05d}.dcm".format(
                                    prefix, number,
                                    scans[number][image][echo]["acquisition_nr"],
                                    image)
                                if tbv_files not in scans[number][image][echo]["filename"]:
                                    os.link(os.path.join(
                                        dicom_folder,
                                        os.path.split(
                                            scans[number][image][echo]["filename"])[-1]),
                                            os.path.join(bv_folder, target_name))

                    except:
                        warnings += "\nError creating Brain Voyager links "

            # Logfiles
            if type != "anat":
                dialogue.update(
                    status=["Measurement {0} ({1} of {2})".format(
                        number, meas_counter+1, len(self.measurements)),
                        "Copying logfiles..."])
                if run_as_action:
                    while self.master.tk.dooneevent(_tkinter.DONT_WAIT):
                        pass

                try:
                    warning = measurement[4].copy_logfiles(d, name_folder)
                    if warning != None:
                        warnings += warning

                except:
                    warnings += "\nError copying logfiles " \
                        "for measurement {0}\n".format(number)

        # TBV Files
        if tbv_links == True:
            dialogue.update(status=["Finalization",
                                    "Copying Turbo-BrainVoyager files..."])
            if run_as_action:
                while self.master.tk.dooneevent(_tkinter.DONT_WAIT):
                    pass

            try:
                tbv_folder = os.path.join(session_folder, "TBV")

                tbv_file_list = []
                for path, dirs, files in os.walk(os.path.abspath(
                        os.path.join(d, tbv_files))):
                    for name in files:
                        tbv_file_list.append(os.path.join(path, name))

                for counter, src in enumerate(tbv_file_list):
                    rel_dst = os.path.relpath(src, (os.path.abspath(d)))
                    dst = os.path.abspath(os.path.join(tbv_folder, rel_dst))

                    if not os.path.exists(os.path.split(dst)[0]):
                        os.makedirs(os.path.split(dst)[0])

                    percentage = int(round(
                            (float(counter) + 1) / len(tbv_file_list) * 100))
                    dialogue.update(
                        status=[
                            "Finalization",
                            "Copying Turbo-BrainVoyager files...{0}%".format(
                                percentage)])
                    if run_as_action:
                        self.master.tk.dooneevent(_tkinter.DONT_WAIT)

                    shutil.copyfile(src, dst)

            except:
                warnings += "\nError copying Turbo Brain Voyager files "

            # Create dcm links
            dialogue.update(status=["Finalization",
                                    "Creating Turbo-BrainVoyager links..."])
            if run_as_action:
                while self.master.tk.dooneevent(_tkinter.DONT_WAIT):
                    pass

            try:
                tbv_runs = []
                files = glob.glob(os.path.join(tbv_folder, tbv_files, "*.tbv"))
                tbvj = False
                if files == []:
                    files = glob.glob(os.path.join(tbv_folder, tbv_files,
                                                   "*.tbvj"))
                    tbvj = True

                for filename in files:
                    with open(filename) as f:
                        if tbvj:
                            data = json.loads(f.read())
                            run_nr = int(
                                data["DataFormatInfo"]["DicomFirstVolumeNr"])
                            run_folder_name = data["Title"]
                        else:
                            for line in f.readlines():
                                # if line.startswith("DicomFirstVolumeNr"):
                                #     run_nr = int(line.split()[-1])
                                if "DicomFirstVolumeNr" in line:
                                    run_nr = int(line.split()[-1].strip(','))
                                # if line.startswith("Title:"):
                                #     run_folder_name = line.split()[-1].replace('"',
                                #                                                '')
                                if "Title" in line:
                                    run_folder_name = line.split()[-1].strip(
                                        ',').replace('"', '')

                        tbv_runs.append([run_folder_name, run_nr])

                tbv_runs.sort(key = lambda x: x[1])
                session_func = os.path.join(session_folder, "func")

                links = []
                for run_nr, run in enumerate(tbv_runs):
                    run_folder = glob.glob(os.path.join(
                        session_func, '{:03d}-{}*'.format(run[1], tbv_prefix)))
                    if run_folder != []:
                        run_folder = run_folder[0]
                        source_folder = os.path.abspath(os.path.join(
                                        run_folder, "DICOM"))

                        for volume, image in enumerate(sorted(os.listdir(
                                source_folder))):
                            target_name = "001_{:06d}_{:06d}.dcm".format(
                                run[1], volume + 1)
                            links.append(
                                [os.path.join(source_folder, image),
                                 os.path.join(tbv_folder, target_name)])

                        # Change absolute path for prt file to relative path in fmr file
                    try:
                        if run[0] in os.listdir(os.path.join(tbv_folder,
                                                             tbv_files)):
                            fmr_file = os.path.abspath(
                                os.path.join(tbv_folder, tbv_files, run[0],
                                             "{}.fmr").format(
                                                 run[0]))
                            with open(fmr_file) as f:
                                for line in f.readlines():
                                    if line.startswith("ProtocolFile"):
                                        prt_path = line.split()[-1]

                            replace(fmr_file, prt_path,
                                    '"./../{}.prt"'.format(run[0]))
                    except:
                        warnings += "\nError adjusting the protocol path in fmr file for Turbo Brain Voyager "

                for counter, link in enumerate(links):
                    percentage = int(round((float(counter)) / len(links) * 100))
                    dialogue.update(
                        status=["Finalization",
                                "Creating Turbo-BrainVoyager links...{0}%".format(
                                    percentage)])
                    if run_as_action:
                        self.master.tk.dooneevent(_tkinter.DONT_WAIT)

                    os.link(link[0], link[1])

            except:
                warnings += "\nError creating dcm links for Turbo Brain Voyager "

        # Session Files
        dialogue.update(status=["Finalization", "Copying files..."])
        if run_as_action:
            while self.master.tk.dooneevent(_tkinter.DONT_WAIT):
                pass

        try:
            warning = self.files.copy_logfiles(d, session_folder)
            if warning != None:
                warnings += warning
        except:
            warnings += "\nError copying Files "

        # Try general documents
        try:
            all_documents = 0
            total_logs = []

            for measurement in self.measurements:
                original = measurement[4].get(1.0, END)
                logfiles = original.split("\n")
                logfiles = [x.strip() for x in logfiles if x != ""]
                total_logs.extend(logfiles)
            for file in glob.glob(os.path.join(d, "*")):
                if os.path.split(file)[-1] not in total_logs and \
                    os.path.splitext(file)[-1] in (".txt",
                                                   ".pdf",
                                                   ".odt"
                                                   ".doc",
                                                   ".docx"):
                    dialogue.update()
                    if run_as_action:
                        while self.master.tk.dooneevent(_tkinter.DONT_WAIT):
                            pass

                    all_documents += 1
                    shutil.copy(os.path.abspath(file), session_folder)

            if all_documents == 0:
                warnings += "\nNo general documents found\n"
        except:
            warnings += "\nError copying general documents\n"

        # Save scan protocol
        try:
            path = os.path.join(session_folder, self.get_filename() + ".txt")
            self.save(path)
        except:
            warnings += "\nError saving scan protocol\n"

        # Confirm archiving
        self.message = "Archived to: {0}".format(os.path.abspath(folder))
        self.message += warnings

    def archive(self, *args):
        """Archive the data."""

        if self.run_actions is not None and "archive" in self.run_actions:
            archiving = self.run_actions["archive"]
            run_as_action = True
        else:
            dialogue = ArchiveDialogue(self.master)

            archiving = dialogue.get()
            run_as_action = False
        if archiving[0]:
            if os.path.isdir(archiving[1]) and os.path.isdir(archiving[2]):
                self.set_title("Busy")
                self.measurements_frame.unbind_mouse_wheel()
                self.busy_dialogue = BusyDialogue(self)
                self.busy_dialogue.update()
                self.message = ""
                if run_as_action:
                    self._archive_runs(archiving[1:], self.busy_dialogue)
                else:
                    thread = threading.Thread(target=self._archive_runs,
                                              args=[archiving[1:],
                                                    self.busy_dialogue])
                    thread.daemon = True
                    thread.start()
                    self.wait_archiving(thread)

    def wait_archiving(self, thread):
        if thread.is_alive():
            self.master.after(100, lambda:self.wait_archiving(thread))
        else:
            self.busy_dialogue.destroy()
            self.set_title()
            MessageDialogue(self.master, self.message)
            self.measurements_frame.bind_mouse_wheel()
