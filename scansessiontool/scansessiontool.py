"""Scan Session Tool.

A tool for MR scan session documentation and data archiving.

"""


import sys
import os
import platform
import time
import glob
import shutil
import threading
import multiprocessing
from tempfile import mkstemp

if sys.version[0] == '3':
    from tkinter import *
    from tkinter.ttk import *
    from tkinter import font as tkFont
    from tkinter import filedialog as tkFileDialog
    from tkinter import messagebox as tkMessageBox
    from tkinter.scrolledtext import ScrolledText
else:
    from Tkinter import *
    from ttk import *
    import tkFont
    import tkFileDialog
    import tkMessageBox
    from ScrolledText import ScrolledText

import yaml
import pydicom

from .__meta__ import __version__, __date__


docs = """
+ - - - - - - - - - - - - - - Scan Session Tool - - - - - - - - - - - - - - +
|                                                                           |
|        A tool for MR scan session documentation and data archiving        |
|                                                                           |
|             Authors: Florian Krause <f.krause@donders.ru.nl>              |
|                      Nikos Kogias <n.kogias@student.ru.nl>                |
|                                                                           |
+ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - +



=================================== About ===================================

The Scan Session Tool is a graphical application for documenting (f)MRI scan
sessions and automatized data archiving. Information about the scan session
itself, used forms and documents, as well as the single measurements can be
entered and saved into a protocol file. This information can furthermore be
used to copy acquired data (DICOM images as well as optional stimulation
protocols and logfiles into a specific hierarchical folder structure for
unified archiving purposes, with optional sepcial support for
(Turbo-)BrainVoyager (https://brainvoyager.com).



=================================== Usage ===================================

The user interface is organized into three different content areas, each hol-
ding different information about the scan session, as well as an additional
control area for opening and saving session information and for automatically
archiving acquired data, based on the session information.


----------------------- The "General Information" area ----------------------

This area provides input fields for basic information about the scan session.
Some of the fields allow for a selection of pre-specified values taken from
a config file (see below), while others take freely typed characters. Fields
that are marked with a red background, are mandatory and need to be filled
in. Fields that are marked with an orange background are automatically filled
in, but need to be checked.
The following fields are available:
    "Project"        - The project identifier
                       (free-type and selection)
    "Subject"        - The subject number
                       (001-999)
                     - The subject type
                       (free-type and selection)
    "Session"        - The session number
                       (001-999)
                     - The session type
                       (free-type and selection)
    "Date"           - The date of the scan session
                       (free-type, auto-filled)
    "Time A"         - The main time period (e.g. official scanner booking)
                       (free-type)
    "Time B"         - An additional time period (e.g. actual scanner usage)
                       (free-type)
    "User 1"         - The main user (e.g. responsible MR operator)
                       (free-type and selection)
    "User 2"         - An additional user (e.g. back-up/buddy)
                       (free-type and selection)
    "Notes"          - Any additional notes about the session
                       (free-type)


--------------------------- The "Documents" area ----------------------------

This area provides input fields for additional documents that are acquired
during the session, such as logfiles and behavioural data files, as well as
questionnaires and forms that are filled in by the participant. The
following input fields are available:
    "Files"       - A newline separated list of all session logfiles and ad-
                    ditional documents; wildcard masks (*) will be completed
                    during archiving
                    (free-type)
    "Checklist"   - Checkboxes to specify which forms and documents have been
                    collected from the participant. Additional documents can
                    be specified in a configuration file (see "Config File"
                    section). The following checkboxes are available:
                    "MR Safety Screening Form"            - The (f)MRI scree-
                                                            ning from provi-
                                                            ded by the scan-
                                                            ning institution
                    "Participation Informed Consent Form" - The official MRI
                                                            written consent
                                                            form


------------------------- The "Measurements" area ---------------------------

This area provides several input fields for each measurement of the session.
When starting the application, only one (empty) measurement is shown. Click-
ing on "Add Measurement" will create additional measurements. Fields that are
marked with a red background, are mandatory and need to be filled in. Fields
that are marked with an orange background are automatically filled in, but
need to be checked.
The following input fields are available per measurement:
    "No"                   - The number of the measurement
                             (001-999)
    "Type"                 - "anat", "func" or "misc"
                             (selection)
    "Vols"                 - The number of volumes of the measurement
                             (free-type)
    "Name"                 - The name of the measurement
                             (free-type, selection)
    "Logfiles"             - A newline separated list of all connected
                             logfiles; wildcard masks (*) will be completed
                             during archiving (please note that a stimulation
                             protocol mask will be included automatically,
                             based on the session information)
                             (free-type)
    "Comments"             - Any additional comments about the measurement
                             (free-type)


----------------------------- The control area ------------------------------

The control area consists of the following three buttons:
    "Open"    - Opens previously saved information from a text file
    "Save"    - Saves the entered session information into a text file
    "Archive" - Copies acquired data from a specified source folder into a
                target folder at another specified location. Please note that
                all data are expected to be within the specified source fol-
                der. That is, all DICOM files (*.dcm OR *.IMA; with or with-
                out sub-folders), all stimulation protocols and all logfiles.
                Optionally, links to the DICOM images in BrainVoyager and
                Turbo-BrainVoyager formats can be created. Turbo-BrainVoyager
                files and data will be manipulated to work in the target
                directory.
                The data will be copied into the following folder hierarchy:
                    DICOMs -->
                      <Project>/sub-<Subject>/ses-<Session>/<Type>/
                      <No>-<Name>/<DICOM>/
                    Logfiles -->
                      <Project>/sub-<Subject>/ses-<Session>/<Type>/
                      <No>-<Name>/
                    Files -->
                      <Project>/sub-<Subject>/ses-<Session>/
                    BrainVoyager files (links only, optional) -->
                      <Project>/sub-<Subject>/ses-<Session>/<BV>/
                    Turbo-BrainVoyager files (links only, optional) -->
                      <Project>/sub-<Subject>/ses-<Session>/<TBV>/
                    Scan Session Protocol -->
                      <Project>/sub-<Subject>/ses-<Session>/


================================ Config File ================================

A configuration file can be created to pre-define the values to be used as
selection options for the "Subject", "Session", "Certified User", "Backup
Person", "Notes", the measurement "Name", "Vols" and "Comments" on a per
project basis, as well as additional items in the "Files" and "Checklist"
fields of the "Documents" section. The Scan Session Tool will look for a con-
figuration file with the name "sst.yaml", located in the current working di-
rectory or in the $HOME folder.

The syntax is YAML. Here is an example:

Project 1:
    SubjectTypes:
        - Group1
        - Group2

    SessionTypes:
        - Sess1
        - Sess2

    Users:
        - User1
        - User2

    Backups:
        - User1
        - User2

    Notes: |
           Subject details
           ---------------

           Age:
           Gender: m[ ] f[ ]

    Files:
        - "*.txt"

    Checklist:
        - Pre-Scan Questionnaire
        - Post-Scan Questionnaire

    Measurements anat:
        - Name:        Localizer
          Vols:        3

        - Name:        Anatomy
          Vols:        192

    Measurements func:
        - Name:        Run1
          Vols:        300
          Comments:    |
                       Answer 1:

        - Name:        Run2
          Vols:        400
          Comments:    |
                       Answer 2:

        - Name:        Run3
          Vols:        200
          Comments:    |
                       Answer 3:

    Measurements misc:
        - Name:        Run1incomplete
          Vols:
          Comments:


Project 2:
    SubjectTypes:
        - GroupA
        - GroupB

    SessionTypes:
        - SessA
        - SessB

    Users:
        - UserA
        - UserB

    Backups:
        - UserA
        - UserB

    Notes: |
           Subject details
           ---------------

           Age:
           Gender: m[ ] f[ ]

    Files:
        - "*.txt"

    Checklist:
        - Participation Reimbursement Form

    Measurements anat:
        - Name:        Localizer
          Vols:        3

        - Name:        MPRAGE
          Vols:        192

    Measurements func:
        - Name:        RunA
          Vols:        300
          Comments:    |
                       Answer 1:

        - Name:        RunB
          Vols:        400
          Comments:    |
                       Answer 2:

        - Name:        RunC
          Vols:        200
          Comments:    |
                       Answer 3:

    Measurements misc:
        - Name:        RunAImcomplete
          Vols:
          Comments:
"""

def replace(file_path, pattern, subst):

    # Create temp file
    fh, abs_path = mkstemp()
    new_file = open(abs_path,'w')
    old_file = open(file_path)
    for line in old_file:
        new_file.write(line.replace(pattern, subst))
    # Close temp file
    new_file.close()
    os.close(fh)
    old_file.close()
    # Remove original file
    os.remove(file_path)
    # Move new file
    shutil.move(abs_path, file_path)


class FixedSizeFrame(Frame):
    def __init__(self, master, width, height, **kw):
        Frame.__init__(self, master, **kw)
        self["width"] = width
        self["height"] = height
        self.grid_propagate(False)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)


class AutoScrollbarText(Text):
    def __init__(self, master=None, **kw):
        self.frame = Frame(master)
        self.yvbar = Scrollbar(self.frame)
        self.yvbar.grid(row=0, column=1, sticky="NS")

        kw.update({'yscrollcommand': self.set_yvbar})
        Text.__init__(self, self.frame, undo=True, **kw)
        self.grid(row=0, column=0, sticky="WENS")
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.yvbar['command'] = self.yview

        self.undo_history = 0
        if platform.system() == "Darwin":
            self.bind("<Command-z>", self.undo_dummy)
            self.bind("<Command-Z>", self.redo)
        else:
            self.bind("<Control-z>", self.undo_dummy)
            self.bind("<Control-Z>", self.redo)

        # Copy geometry methods of self.frame without overriding Text
        # methods -- hack!
        text_meths = list(vars(Text).keys())
        methods = list(vars(Pack).keys()) + list(vars(Grid).keys()) + \
                list(vars(Place).keys())
        methods = set(methods).difference(text_meths)

        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.frame, m))

    def undo_dummy(self, *args):
        if self.edit_modified():
            self.undo_history += 1

    def redo(self, *args):
        if self.undo_history > 0:
            self.edit_redo()
            self.undo_history -= 1

    def set_yvbar(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            # grid_remove is currently missing from Tkinter!
            self.yvbar.tk.call("grid", "remove", self.yvbar)
        else:
            self.yvbar.grid()
        self.yvbar.set(lo, hi)

    def __str__(self):
        return str(self.frame)

    def copy_logfiles(self, source, destination):
        original = self.get(1.0, END)
        logfiles = original.split("\n")
        logfiles = [x.strip() for x in logfiles if x != ""]
        warning = ""
        new = original
        for logfile in logfiles:
            if "*" in logfile:
                replaced = []
            try:
                if logfile != "" and not os.path.isdir(logfile):
                    files = glob.glob(os.path.join(source, logfile))
                    if files == []:
                        raise Exception
                    for file_ in files:
                        if not os.path.isdir(file_):
                            if "*" in logfile:
                                replaced.append(
                                    os.path.split(file_)[-1])
                            shutil.copyfile(
                                file_,
                                os.path.join(destination,
                                             os.path.split(file_)[-1]))
                    if "*" in logfile:
                        new = new.replace(
                            logfile, "\n".join(replaced))
                        self.delete(1.0, END)
                        self.insert(1.0, new)

                if logfile != "" and os.path.isdir(os.path.join(source,
                                                                logfile)):
                    shutil.copytree(os.path.abspath(os.path.join(source,
                                                                 logfile)),
                                    os.path.abspath(os.path.join(destination,
                                                                 logfile)))
            except:
               warning += "\nError copying logfiles " \
                   "'{}' not found\n".format(logfile)
        return warning


class VerticalScrolledFrame(Frame):
    """A pure Tkinter scrollable frame that actually works!

    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling

    """
    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)

        # Create a canvas object and a vertical scrollbar for scrolling it
        self.vscrollbar = Scrollbar(self, orient=VERTICAL)
        self.vscrollbar.pack(fill=Y, side=RIGHT, expand=TRUE)
        self.canvas = Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=self.vscrollbar.set,
                        width=self.winfo_reqwidth(),
                        height=self.winfo_reqheight(), background="grey")
        self.canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        self.vscrollbar.config(command=self.canvas.yview)

        # Reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # Create a frame inside the canvas which will be scrolled with it
        style = Style()
        style.configure("Grey.TFrame", background="darkgrey")
        self.interior = Frame(self.canvas, width=self.winfo_reqwidth(),
                              style="Grey.TFrame")
        self.interior.grid_rowconfigure(0, weight=1)
        self.interior.grid_columnconfigure(0, weight=1)
        self.interior_id = self.canvas.create_window(0, 0,
                                                     window=self.interior,
                                                     anchor=NW)

        self.interior.bind('<Configure>', self._configure_interior)

        self.bind('<Enter>', self.bind_mouse_wheel)
        self.bind('<Leave>', self.unbind_mouse_wheel)

    def bind_mouse_wheel(self, *args):
        os = platform.system()
        self.bind_ids = []
        if os == "Linux":
            self.bind_ids.append(self.vscrollbar.bind_all("<4>",
                                                      self._on_mousewheel))
            self.bind_ids.append(self.vscrollbar.bind_all("<5>",
                                                      self._on_mousewheel))
        else:
            self.bind_ids.append(self.vscrollbar.bind_all("<MouseWheel>",
                                                      self._on_mousewheel))

    def unbind_mouse_wheel(self, *args):
        try:
            for x in self.bind_ids:
                os = platform.system()
                if os == "Linux":
                    self.vscrollbar.unbind("<4>", x)
                    self.vscrollbar.unbind("<5>", x)
                else:
                    self.vscrollbar.unbind("<MouseWheel>", x)
        except:
            pass

    # track changes to the canvas and frame width and sync them,
    # also updating the scrollbar
    def _configure_interior(self, event):
        # Update the scrollbars to match the size of the inner frame
        if self.interior.winfo_reqheight() < self.winfo_reqheight():
            size = (self.interior.winfo_reqwidth(),
                    self.winfo_reqheight())
        else:
            size = (self.interior.winfo_reqwidth(),
                    self.interior.winfo_reqheight())
        self.canvas.config(scrollregion="0 0 %s %s" % size)

    def _configure_canvas(self, event):
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            # Update the inner frame's width to fill the canvas
            self.canvas.itemconfigure(self.interior_id,
                                      width=self.canvas.winfo_width())

    def _on_mousewheel(self, event):
        os = platform.system()
        if os == "Linux":
            if event.num == 4:
                self.canvas.yview_scroll(-2, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(2, "units")
        elif os == "Darwin":
            self.canvas.yview_scroll(-2*event.delta, "units")
        elif os == "Windows":
            if sys.version[0] == '3':
                self.canvas.yview_scroll(-2*(event.delta//120), "units")
            else:
                self.canvas.yview_scroll(-2*(event.delta/120), "units")


class AutocompleteCombobox(Combobox):

    def set_completion_list(self, completion_list):
        self._completion_list = sorted(completion_list, key=str.lower)
        self._hits = []
        self._hit_index = 0
        self.position = 0
        self.bind('<KeyRelease>', self.handle_keyrelease)
        self['values'] = self._completion_list

    def autocomplete(self, delta=0):
        if delta:  # delete selection, otherwise we would fix current position
            self.delete(self.position, END)
        else:  # set position to end so selection starts where textentry ended
            self.position = len(self.get())
        # Collect hits
        _hits = []
        for element in self._completion_list:
            if element.lower().startswith(self.get().lower()):
                _hits.append(element)
        # If we have a new hit list, keep this in mind
        if _hits != self._hits:
            self._hit_index = 0
            self._hits = _hits
        # Only allow cycling if we are in a known hit list
        if _hits == self._hits and self._hits:
            self._hit_index = (self._hit_index + delta) % len(self._hits)
        # Now finally perform the auto completion
        if self._hits:
            self.delete(0, END)
            self.insert(0, self._hits[self._hit_index])
            self.select_range(self.position, END)

    def handle_keyrelease(self, event):
        """event handler for the keyrelease event on this widget"""
        if event.keysym == "BackSpace":
            self.delete(self.index(INSERT), END)
            self.position = self.index(END)
        elif event.keysym == "Left":
            self.position = self.position - 1  # delete one character
        elif event.keysym == "Right":
            self.position = self.index(END)  # go to end (no selection)
        elif len(event.keysym) == 1:
            self.autocomplete()
            # No need for up/down, we'll jump to the popup
            # list at the position of the autocompletion

class Spinbox(Entry):
    def __init__(self, master=None, **kw):
        s = Style()
        Entry.__init__(self, master, "ttk::spinbox", **kw)

    def current(self, newindex=None):
        return self.tk.call(self._w, 'current', newindex)

    def set(self, value):
        return self.tk.call(self._w, 'set', value)


class App(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)

        font = tkFont.nametofont("TkDefaultFont")
        font.config(family="Arial", size=-13)
        self.default_font = font.cget("family")
        self.default_font_size = font.cget("size")
        self.font = (self.default_font, self.default_font_size)

        style = Style()
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

        self.menubar = Menu(master)
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
        master["menu"] = self.menubar

        master.rowconfigure(0, weight=1)
        master.columnconfigure(0, weight=1)
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
            path = None
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
        """Save the data."""

        if filename is None:
            filename = self.get_filename()
            f = tkFileDialog.asksaveasfile(mode='w', defaultextension='.txt',
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
                f.write("{0}{1}{2}\n".format(label, " "*(24-len(label)),
                                             value))

        f.write("\nNotes:")
        notes = self.general_widgets[-1].get(1.0, END).split("\n")
        notes_lines = [x.strip() for x in notes]
        try:
            for line_nr, line in enumerate(notes_lines):
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
                f.write("{0}:{1}{2}\n".format(
                    self.measurement[elem],
                    " "*(23-len(self.measurement[elem])),
                    value))

            f.write("\nComments:")

            comments = m[-1].get(1.0, END).split("\n")
            comment_lines = [x.strip() for x in comments if x != ""]
            try:
                for line_nr, line in enumerate(comment_lines):
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
        """Load data."""

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
                            else:
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
                        else:
                            self.measurements[len(measurement_starts)-
                                              1][-1].insert(
                                                  END,
                                                  "\n" + line[24:].strip())

            self.disable_save()

    def set_title(self, status=None):
        if status is None:
            self.master.title('Scan Session Tool')
        else:
            self.master.title('Scan Session Tool ({0})'.format(status))

    def _archive_runs(self, archiving, dialogue):
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
        all_dicoms = []
        for root, _, files in os.walk(d):
            for f in files:
                if os.path.splitext(f)[-1] in (".dcm", ".IMA"):
                    all_dicoms.append(os.path.join(root, f))

        imap = multiprocessing.Pool().imap_unordered

        scans = {}  # scans[RUN][VOLUME]["protocolname"|"filename"]
        for counter, dicom in enumerate(imap(_readdicom, all_dicoms)):
            percentage = int(
                round((float(counter) + 1) / len(all_dicoms) * 100))
            dialogue.update(
                status=["Preparation",
                        "Reading DICOM images...{0}%".format(percentage)])
            try:
                scans[dicom[1]]
            except KeyError:
                scans[dicom[1]] = {}
            scans[dicom[1]][dicom[2]] = \
                {"protocolname": dicom[3],
                 "filename": dicom[0]}

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
            elif len(scans[number]) != vols:
                warnings += "\nError copying images for measurement {0}:" \
                            "    'Vols' unequals number of images\n".format(
                                number)
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
                try:
                    dicom_folder = os.path.join(name_folder, "DICOM")
                    if not os.path.exists(dicom_folder):
                        os.makedirs(dicom_folder)

                    for counter, image in enumerate(scans[number]):
                        percentage = int(round(
                            (float(counter) + 1) / len(scans[number]) * 100))
                        dialogue.update(
                            status=["Measurement {0} ({1} of {2})".format(
                                number, meas_counter + 1,
                                len(self.measurements)),
                                    "Copying DICOM files...{0}%".format(
                                        percentage)])
                        shutil.copyfile(
                            scans[number][image]["filename"], os.path.join(
                                dicom_folder, os.path.split(
                                    scans[number][image]["filename"])[-1]))
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
                    try:
                        bv_folder = os.path.join(session_folder, "BV")
                        if not os.path.exists(bv_folder):
                            os.makedirs(bv_folder)

                        for counter, image in enumerate(scans[number]):
                            percentage = int(round((float(counter) + 1) / len(
                                scans[number]) * 100))
                            dialogue.update(
                                status=["Measurement {0} ({1} of {2})".format(
                                    number, meas_counter + 1,
                                    len(self.measurements)),
                                        "Creating BrainVoyager links...{0}%".format(
                                            percentage)])
                            target_name = "{}-{:04d}-0001-{:05d}.dcm".format(
                                scans[number][image]["protocolname"],
                                number, image)
                            os.link(os.path.join(
                                dicom_folder,
                                os.path.split(
                                    scans[number][image]["filename"])[-1]),
                                    os.path.join(bv_folder, target_name))

                    except:
                        warnings += "\nError creating Brain Voyager links "

            # Logfiles
            if type != "anat":
                dialogue.update(
                    status=["Measurement {0} ({1} of {2})".format(
                        number, meas_counter+1, len(self.measurements)),
                        "Copying logfiles..."])
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
            if True:
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
                    shutil.copyfile(src, dst)

            else:
                warnings += "\nError copying Turbo Brain Voyager files "

            # Create dcm links
            dialogue.update(status=["Finalization",
                                    "Creating Turbo-BrainVoyager links..."])
            try:
                tbv_runs = []
                tbv_run = 0
                files = glob.glob(os.path.join(tbv_folder, tbv_files, "*.tbv"))
                if files == []:
                    files = glob.glob(os.path.join(tbv_folder, tbv_files, "*.tbvj"))

                for filename in files:
                    with open(filename) as f:
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

                        if os.path.isdir(os.path.join(tbv_folder, tbv_files,
                                                      run_folder_name)):
                            tbv_runs.append([run_folder_name, run_nr])

                tbv_runs.sort(key = lambda x: x[1])
                session_func = os.path.join(session_folder, "func")
                for run in os.listdir(session_func):
                    if run.split("-")[1].startswith(tbv_prefix):
                        source_folder = os.path.abspath(os.path.join(
                            session_func, run, "DICOM"))
                        for volume, image in enumerate(sorted(os.listdir(
                                source_folder))):
                            target_name = "001_{:06d}_{:06d}.dcm".format(
                                tbv_runs[tbv_run][1], volume + 1)
                            os.link(os.path.join(source_folder, image),
                                    os.path.join(tbv_folder, target_name))

                        # Change absolute path for prt file to relative path in fmr file
                        try:
                            title = tbv_runs[tbv_run][0]
                            fmr_file = os.path.abspath(os.path.join(
                                tbv_folder, tbv_files, title, "{}.fmr").format(
                                    title))
                            with open(fmr_file) as f:
                                for line in f.readlines():
                                    if line.startswith("ProtocolFile"):
                                        prt_path = line.split()[-1]

                            replace(fmr_file, prt_path, '"./../{}.prt"'.format(
                                title))
                        except:
                            warnings += "\nError adjusting the protocol path in fmr file for Turbo Brain Voyager "
                        tbv_run +=1
                        percentage = int(round(
                                    (float(tbv_run)) / len(tbv_runs) * 100))
                        dialogue.update(
                        status=["Finalization",
                                "Creating Turbo-BrainVoyager links...{0}%".format(
                                    percentage)])

            except:
                warnings += "\nError creating dcm links for Turbo Brain Voyager "

        # Session Files
        dialogue.update(status=["Finalization", "Copying files..."])
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

        dialogue = ArchiveDialogue(self.master)
        archiving = dialogue.get()
        if archiving[0]:
            if os.path.isdir(archiving[1]) and os.path.isdir(archiving[2]):
                self.set_title("Busy")
                self.measurements_frame.unbind_mouse_wheel()
                self.busy_dialogue = BusyDialogue(self.master)
                self.busy_dialogue.update()
                self.message = ""
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


class ArchiveDialogue:

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
        if sys.platform == "win32":
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
        if sys.platform == "win32":
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

    def __init__(self, master):
        self.master = master
        top = self.top = Toplevel(master, background="#49d042")
        try:
            top.attributes('-type', 'splash')
        except:
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

        top.transient(master)
        top.focus_set()
        top.wait_visibility()
        top.grab_set()
        self.bind_id = self.master.bind("<Configure>", self.bring_to_top)
        if sys.platform == "win32":
            master.wm_attributes("-disabled", True)
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
        if sys.platform == "win32":
            self.master.wm_attributes("-disabled", False)
        self.master.focus_set()
        self.master.unbind("<Configure>", self.bind_id)
        self.top.destroy()


class MessageDialogue:

    def __init__(self, master, message):
        self.master = master
        top = self.top = Toplevel(master, background="grey85")
        top.title("Archiving Report")

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
        if sys.platform == "win32":
            master.wm_attributes("-disabled", True)

    def ok(self):
        if sys.platform == "win32":
            self.master.wm_attributes("-disabled", False)
        self.top.grab_release()
        self.top.destroy()


class HelpDialogue:

    def __init__(self, master):
        self.master = master
        top = self.top = Toplevel(master, background="grey85")
        top.title("Help")
        top.resizable(False, False)

        self.text = ScrolledText(top, width=77)
        self.text.pack()
        self.text.insert(END, docs)
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
        if sys.platform == "win32":
            master.wm_attributes("-disabled", True)
        master.wait_window(top)

    def ok(self, *args):
        if sys.platform == "win32":
            self.master.wm_attributes("-disabled", False)
        self.top.grab_release()
        self.top.destroy()


def _readdicom(filename):
    dicom = pydicom.filereader.read_file(filename, stop_before_pixels=True)
    return [filename, dicom.SeriesNumber, dicom.InstanceNumber,
            dicom.ProtocolName]

def _copyfile(source_dict, target_folder):
    shutil.copyfile(source_dict["filename"], os.path.join(
            target_folder, os.path.split(source_dict["filename"])[-1]))

def run():
    root = Tk()
    style = Style()
    style.theme_use("default")
    root.resizable(False, False)
    root.option_add('*tearOff', FALSE)
    app = App(master=root)
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
