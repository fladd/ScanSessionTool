#!/usr/bin/env python

__version__ = '0.4.0'
__date__ = '16 Dec 2014'


import os
import platform
import time
import glob
import shutil
from tempfile import mkstemp
from Tkinter import *
from ttk import *
from ScrolledText import ScrolledText
import tkFont
import tkFileDialog
import tkMessageBox


def replace(file_path, pattern, subst):

    #Create temp file
    fh, abs_path = mkstemp()
    new_file = open(abs_path,'w')
    old_file = open(file_path)
    for line in old_file:
        new_file.write(line.replace(pattern, subst))
    #close temp file
    new_file.close()
    os.close(fh)
    old_file.close()
    #Remove original file
    os.remove(file_path)
    #Move new file
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
        #self.xvbar = Scrollbar(self.frame, orient="horizontal")
        self.yvbar.grid(row=0, column=1, sticky="NS")
        #self.xvbar.grid(row=1, column=0, sticky="WE")

        kw.update({'yscrollcommand': self.set_yvbar})
        #kw.update({'xscrollcommand': self.set_xvbar})
        Text.__init__(self, self.frame, **kw)
        self.grid(row=0, column=0, sticky="WENS")
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.yvbar['command'] = self.yview
        #self.xvbar['command'] = self.xview

        # Copy geometry methods of self.frame without overriding Text
        # methods -- hack!
        text_meths = vars(Text).keys()
        methods = vars(Pack).keys() + vars(Grid).keys() + vars(Place).keys()
        methods = set(methods).difference(text_meths)

        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.frame, m))

    def set_yvbar(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            # grid_remove is currently missing from Tkinter!
            self.yvbar.tk.call("grid", "remove", self.yvbar)
        else:
            self.yvbar.grid()
        self.yvbar.set(lo, hi)

    # def set_xvbar(self, lo, hi):
    #     print lo, hi
    #     if float(lo) <= 0.0 and float(hi) >= 1.0:
    #         # grid_remove is currently missing from Tkinter!
    #         self.xvbar.tk.call("grid", "remove", self.xvbar)
    #     else:
    #         self.xvbar.grid()
    #     self.xvbar.set(lo, hi)

    def __str__(self):
        return str(self.frame)


class VerticalScrolledFrame(Frame):
    """A pure Tkinter scrollable frame that actually works!

    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling

    """
    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
        self.vscrollbar = Scrollbar(self, orient=VERTICAL)
        self.vscrollbar.pack(fill=Y, side=RIGHT, expand=TRUE)
        self.canvas = Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=self.vscrollbar.set,
                        width=self.winfo_reqwidth(),
                        height=self.winfo_reqheight(), background="grey")
        self.canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        self.vscrollbar.config(command=self.canvas.yview)

        # reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        style = Style()
        style.configure("Grey.TFrame", background="darkgrey")
        self.interior = Frame(self.canvas, width=self.winfo_reqwidth(),
                              style="Grey.TFrame")
        self.interior.grid_rowconfigure(0, weight=1)
        self.interior.grid_columnconfigure(0, weight=1)
        self.interior_id = self.canvas.create_window(0, 0,
                                                     window=self.interior,
                                                     anchor=NW)

        #self.canvas.bind('<Configure>', self._configure_canvas)
        self.interior.bind('<Configure>', self._configure_interior)

        return


    def bind_mouse_wheel(self, *args):
        os = platform.system()
        self.bind_ids = []
        if os == "Linux":
            self.bind_ids.append(self.canvas.bind_all("<4>",
                                                      self._on_mousewheel))
            self.bind_ids.append(self.canvas.bind_all("<5>",
                                                      self._on_mousewheel))
        else:
            self.bind_ids.append(self.canvas.bind_all("<MouseWheel>",
                                                      self._on_mousewheel))

    def unbind_mouse_wheel(self, *args):
        for x in self.bind_ids:
            os = platform.system()
            if os == "Linux":
                self.canvas.unbind("<4>", x)
                self.canvas.unbind("<5>", x)
            else:
                self.canvas.unbind("<MouseWheel>", x)

    # track changes to the canvas and frame width and sync them,
    # also updating the scrollbar
    def _configure_interior(self, event):
        # update the scrollbars to match the size of the inner frame
        if self.interior.winfo_reqheight() < self.winfo_reqheight():
            size = (self.interior.winfo_reqwidth(),
                    self.winfo_reqheight())
        else:
            size = (self.interior.winfo_reqwidth(),
                    self.interior.winfo_reqheight())
        self.canvas.config(scrollregion="0 0 %s %s" % size)
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            # update the canvas's width to fit the inner frame
            #self.canvas.config(width=self.interior.winfo_reqwidth())
            pass

    def _configure_canvas(self, event):
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            # update the inner frame's width to fill the canvas
            self.canvas.itemconfigure(self.interior_id,
                                      width=self.canvas.winfo_width())

    def _on_mousewheel(self, event):
        os = platform.system()
        if os == "Linux":
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")
        elif os == "Darwin":
            self.canvas.yview_scroll(-1*event.delta, "units")
        elif os == "Windows":
            self.canvas.yview_scroll(-1*(event.delta/120), "units")


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
        # collect hits
        _hits = []
        for element in self._completion_list:
            if element.lower().startswith(self.get().lower()):
                _hits.append(element)
        # if we have a new hit list, keep this in mind
        if _hits != self._hits:
            self._hit_index = 0
            self._hits = _hits
        # only allow cycling if we are in a known hit list
        if _hits == self._hits and self._hits:
            self._hit_index = (self._hit_index + delta) % len(self._hits)
        # now finally perform the auto completion
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
            #if self.position < self.index(END):  # delete the selection
            #    self.delete(self.position, END)
            #else:
            self.position = self.position - 1  # delete one character
                #self.delete(self.position, END)
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
        if platform.system() == "Windows":
            font.config(family="Arial", size=11)
        else:
            font.config(family="Arial")
        self.default_font = font.cget("family")
        self.default_font_size = font.cget("size")
        self.font = (self.default_font, self.default_font_size)

        style = Style()
        style.configure("Blue.TLabel", foreground="blue")
        style.configure("Grey.TLabel", foreground="darkgrey")
        style.configure("Header.TLabel", background="darkgrey")
        style.configure("Header.TFrame", background="darkgrey")
        style.configure("Red.TCombobox", fieldbackground="red")
        style.configure("Orange.TCombobox", fieldbackground="orange")
        style.map("Orange.TCombobox", fieldbackground=[("readonly", "orange")])
        style.configure("Red.TEntry", fieldbackground="red")
        style.configure("Orange.TEntry", fieldbackground="orange")
        style.configure("Orange.TSpinbox", fieldbackground="orange")
        style.map("Orange.TSpinbox", fieldbackground=[("disabled", "orange")])

        self.menubar = Menu(master)
        if platform.system() == "Darwin":
            modifier = "Command"
            self.apple_menu = Menu(self.menubar, name="apple")
            self.menubar.add_cascade(menu=self.apple_menu)
            self.apple_menu.add_command(
                label="About Scan Session Tool",
                command=lambda: HelpDialogue(self.master).show())
        else:
            modifier = "Control"
        self.file_menu = Menu(self.menubar)
        self.menubar.add_cascade(menu=self.file_menu, label="File")
        self.file_menu.add_command(label="Save", command=self.save,
                                   accelerator="{0}-S".format(modifier))
        self.file_menu.add_command(label="Load", command=self.load,
                                   accelerator="{0}-L".format(modifier))
        self.master.bind("<{0}-l>".format(modifier), self.load)
        self.file_menu.add_command(label="Archive", command=self.archive,
                                   accelerator="{0}-A".format(modifier))
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
        self.help_menu = Menu(self.menubar)
        self.menubar.add_cascade(menu=self.help_menu, label="Help")
        self.help_menu.add_command(
            label="Scan Session Tool Help",
            command=lambda: HelpDialogue(self.master).show())
        master["menu"] = self.menubar

        master.rowconfigure(0, weight=1)
        master.columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid(sticky="WENS")
        self.general = ("Project:",
                        "Subject No.:",
                        "Group:",
                        "Session:",
                        "Date:",
                        "Booked Time:",
                        "Actual Time:",
                        "Certified User:",
                        "Backup Person:")
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
                                 self.default_font_size + 2,
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
        self.general_frame_left.grid(row=0, column=0, sticky="W", padx=10)
        self.general_frame_right = Frame(self.general_frame)
        self.general_frame_right.grid(row=0, column=1, padx=10, sticky="W")

        for row, x in enumerate(self.general):
            label = Label(self.general_frame_left, text=x)
            #label['font'] = (self.default_font, self.default_font_size,
            #                   "bold")
            label.grid(row=row, column=0, sticky="E", padx=(0, 3), pady=3)
            self.general_labels.append(label)
            var = StringVar()
            var.trace("w", self.change_callback)
            self.general_vars.append(var)
            if row == 1:
                var.set(1)
                spinbox = Spinbox(self.general_frame_left, from_=1, to=999,
                          width=3, justify="right", textvariable=var,
                          state="readonly", font=self.font, style="Orange.TSpinbox")
                spinbox.grid(row=row, column=1, sticky="W")
                self.general_widgets.append(spinbox)
            elif row in (0, 2, 3, 7, 8):
                validate = None
                vcmd = None
                #validate = "key"
                #vcmd = (self.master.register(self.validate),
                #[chr(x) for x in range(127)],
                #49, '%S', '%P')
                if row in (0, 3):
                    combobox = AutocompleteCombobox(self.general_frame_left, textvariable=var,
                                                    validate=validate, validatecommand=vcmd,
                                                    font=self.font, style="Red.TCombobox")
                else:
                    combobox = AutocompleteCombobox(self.general_frame_left, textvariable=var,
                                                    validate=validate, validatecommand=vcmd,
                                                    font=self.font)

                if row == 0:
                    projects = self.config.keys()
                    projects.sort()
                    combobox.set_completion_list(projects)
                combobox.grid(row=row, column=1, sticky="W")
                self.general_widgets.append(combobox)
            elif row in (4, 5, 6):
                if row == 4:
                    validate = "key"
                    vcmd = (self.master.register(self.validate),
                            "0123456789-", 10, '%S', '%P')
                    width = 10
                    self.autofill_date_callback()
                elif row in (5, 6):
                    validate = "key"
                    vcmd = (self.master.register(self.validate),
                            "0123456789:-", 11, '%S', '%P')
                    width = 10
                if row == 4:
                    entry = Entry(self.general_frame_left, width=width,
                                  textvariable=var, validate=validate,
                                  validatecommand=vcmd, font=self.font,
                                  style="Orange.TEntry")
                else:
                    entry = Entry(self.general_frame_left, width=width,
                                  textvariable=var, validate=validate,
                                  validatecommand=vcmd, font=self.font)
                #if row == 4:
                    #entry.bind('<T>', self.autofill_date_callback)
                entry.grid(row=row, column=1, sticky="W")
                self.general_widgets.append(entry)

        notes_label = Label(self.general_frame_right, text="Notes:",
                            style="Green.TLabel")
        notes_label.grid(row=0, column=0, sticky="W")
        #notes_label['font'] = (self.default_font, self.default_font_size,
        #                       "bold")
        notes_container = FixedSizeFrame(self.general_frame_right, 299, 186)
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
                              self.default_font_size + 10,
                              "bold")
        self.nofocus_widgets.append(self.title1)
        self.title2 = Label(self.logo, text="Session",
                           justify="center", style="Blue.TLabel")
        self.title2.grid(row=1)
        self.title2['font'] = (self.default_font,
                              self.default_font_size + 10,
                              "bold")
        self.nofocus_widgets.append(self.title2)
        self.title3 = Label(self.logo, text="Tool",
                           justify="center", style="Blue.TLabel")
        self.title3.grid(row=2)
        self.title3['font'] = (self.default_font,
                              self.default_font_size + 10,
                              "bold")
        self.nofocus_widgets.append(self.title3)
        self.version1 = Label(self.logo,
                             text="Version {0}".format(__version__),
                             style="Grey.TLabel")
        self.version1.grid(row=3)
        self.version1['font'] = (self.default_font, self.default_font_size - 2)
        self.nofocus_widgets.append(self.version1)
        self.version2 = Label(self.logo,
                             text="({0})".format(__date__),
                             style="Grey.TLabel")
        self.version2.grid(row=4)
        self.version2['font'] = (self.default_font, self.default_font_size - 2)
        self.nofocus_widgets.append(self.version2)
        self.help = Button(self.logo, text="?", width=1,
                           command=lambda: HelpDialogue(self.master).show())
        self.help.grid(row=5, pady=5)

        self.button_frame = Frame(self.control_frame)
        self.button_frame.grid(row=1, column=0, padx=10)
        self.nofocus_widgets.append(self.button_frame)
        self.save_button = Button(self.button_frame, text="Save",
                                  command=self.save)
        self.save_button.grid(row=0, column=0, sticky="")
        self.load_button = Button(self.button_frame, text="Load",
                                  command=self.load, state="enabled")
        self.load_button.grid(row=1, column=0, sticky="", pady=3)
        self.go_button = Button(self.button_frame, text="Archive",
                                state="disabled", command=self.archive)
        self.go_button.grid(row=2, column=0, sticky="")

        documents_label = Label(self.top_frame, text="Documents")
        documents_label['font'] = (self.default_font,
                                   self.default_font_size + 2,
                                   "bold")
        self.nofocus_widgets.append(documents_label)
        self.documents_frame = LabelFrame(self.top_frame, text='Documents',
                                          labelwidget=documents_label)
        self.documents_frame.grid(row=0, column=2, sticky="NSE")
        self.nofocus_widgets.append(self.documents_frame)
        self.documents_labels = []
        self.documents_checks = []
        self.documents_vars = []
        for row, x in enumerate(self.documents):
            var = IntVar()
            var.trace("w", self.change_callback)
            check = Checkbutton(self.documents_frame, text=x, variable=var)
            check.grid(sticky="W", padx=10)
            self.documents_vars.append(var)

        self.bottom_frame = Frame(self)
        self.bottom_frame.grid_columnconfigure(0, weight=1)
        self.bottom_frame.grid(row=1, column=0, padx=10, pady=10,
                               sticky="WENS")
        self.nofocus_widgets.append(self.bottom_frame)
        measurements_label = Label(self.bottom_frame, text="Measurements")
        measurements_label['font'] = (self.default_font,
                                      self.default_font_size + 2,
                                      "bold")
        self.nofocus_widgets.append(measurements_label)
        self.measurements_frame1 = LabelFrame(self.bottom_frame,
                                              text='Measurements',
                                              labelwidget=measurements_label)
        self.measurements_frame1.grid_rowconfigure(1, weight=1)
        self.measurements_frame1.grid(row=0, sticky="WENS")
        self.nofocus_widgets.append(self.measurements_frame1)
        self.measurements_frame = VerticalScrolledFrame(
            self.measurements_frame1, height=295, width=989)
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
        label_frame.grid(row=0, columnspan=6, sticky="NS")
        for column, x in enumerate(self.measurement):
            label = Label(label_frame, text=x)
            if column == 0:
                label.grid(row=0, column=column, padx=(18, 0), pady=(3, 3))
            elif column == 1:
                label.grid(row=0, column=column, padx=(45, 0))
            elif column == 2:
                label.grid(row=0, column=column, padx=(39, 0))
            elif column == 3:
                label.grid(row=0, column=column, padx=(76, 0))
            elif column == 4:
                label.grid(row=0, column=column, padx=(195, 0))
            elif column == 5:
                label.grid(row=0, column=column, padx=(243, 130))

            label['font'] = (self.default_font, self.default_font_size,
                             "bold")
            label.bind('<Button-1>', lambda x: app.master.focus())
        self.new_measurement()


    def new_measurement(self, *args):
        #for column, x in enumerate(self.measurement):
        #    label = Label(self.measurements_frame.interior, text=x)
        #    if column == 0:
        #        label.grid(row=0, column=column, padx=(10, 2))
        #    elif column == len(self.measurements) - 1:
        #        label.grid(row=0, column=column, padx=(2, 10))
        #    else:
        #        label.grid(row=0, column=column, padx=2)
        #    label['font'] = (self.default_font, self.default_font_size,
        #                     "bold")
        #    label.bind('<Button-1>', lambda x: app.master.focus())
        value = len(self.measurements) + 1
        scanning_vars = []
        scanning_widgets = []
        var1 = StringVar()
        scanning_vars.append(var1)
        var1.set(value)
        var1.trace("w", self.change_callback)
        spinbox = Spinbox(self.measurements_frame.interior, from_=1, to=99,
                          width=2, justify="right", state="readonly",
                          textvariable=var1, font=self.font,
                          style="Orange.TSpinbox")
        spinbox.grid(row=value, column=0, sticky="W", padx=(10, 2))
        scanning_widgets.append(spinbox)
        var2 = StringVar()
        var2.trace("w", self.change_callback)
        scanning_vars.append(var2)

        #radiobuttons = Frame(self.measurements_frame.interior)
        #radiobuttons.grid(row=value, column=1, sticky="")
        #radio_var = StringVar()
        #radio_var.set("misc")
        #Radiobutton(radiobuttons, text="anat", variable=radio_var,
        #            value="anatomical").pack(anchor="w")
        #Radiobutton(radiobuttons, text="func", variable=radio_var,
        #            value="functional").pack(anchor="w")
        #Radiobutton(radiobuttons, text="misc", variable=radio_var,
        #            value="misc").pack(anchor="w")
        combobox = AutocompleteCombobox(self.measurements_frame.interior,
                            textvariable=var2, width=10, state="readonly",
                            font=self.font, style="Orange.TCombobox")
        combobox.set_completion_list(["anatomical", "functional", "misc"])
        combobox.current(0)
        combobox.grid(row=value, column=1, sticky="", padx=2)
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
        vols.grid(row=value, column=2, sticky="", padx=2)
        scanning_widgets.append(vols)
        var4 = StringVar()
        var4.trace("w", self.change_callback)
        scanning_vars.append(var4)
        validate = None
        vcmd = None
        #validate = "key"
        #vcmd = (self.master.register(self.validate),
        #        [chr(x) for x in range(127)],
        #        49, '%S', '%P')
        name = AutocompleteCombobox(self.measurements_frame.interior,
                                    textvariable=var4, validate=validate,
                                    validatecommand=vcmd, font=self.font,
                                    style="Red.TCombobox")
        name.grid(row=value, column=3, sticky="", padx=2)
        scanning_widgets.append(name)
        #container1 = FixedSizeFrame(self.measurements_frame.interior, 198, 53)
        #container1.grid(row=value, column=4, sticky="NSE", pady=3)
        #prt_file = AutoScrollbarText(container1, state="disabled")
        #prt_file.grid(sticky="WENS")
        #scanning_vars.append(prt_file)
        #scanning_widgets.append(prt_file)
        container2 = FixedSizeFrame(self.measurements_frame.interior, 299, 53)
        container2.grid(row=value, column=4, sticky="NSE", pady=3, padx=2)
        scanning_widgets.append(container2)
        logfiles = AutoScrollbarText(container2, wrap=NONE, background="orange",
                                     highlightbackground="orange")
        logfiles.bind('<KeyRelease>', self.change_callback)
        #logfiles.frame.bind('<Enter>',
        #                lambda event: self.text_mouseover_callback(True))
        #logfiles.frame.bind('<Leave>',
        #                lambda event: self.text_mouseover_callback(False))
        scanning_vars.append(logfiles)  # Needs to be called with START, END!
        logfiles.grid()
        scanning_widgets.append(logfiles)
        container3 = FixedSizeFrame(self.measurements_frame.interior, 299, 53)
        container3.grid(row=value, column=5, sticky="NSE", pady=3, padx=(2, 10))
        scanning_widgets.append(container3)
        text = AutoScrollbarText(container3, wrap=NONE)
        text.bind('<KeyRelease>', self.change_callback)
        #text.frame.bind('<Enter>',
        #                lambda event: self.text_mouseover_callback(True))
        #text.frame.bind('<Leave>',
        #                lambda event: self.text_mouseover_callback(False))
        scanning_vars.append(text)  # Needs to be called with START, END!
        text.grid()
        scanning_widgets.append(text)
        self.measurements.append(scanning_vars)
        self.measurements_widgets.append(scanning_widgets)
        #if value == 6:
        #    self.measurements_frame.bind_mouse_wheel()
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
        for row, x in enumerate(self.config[current_project]["documents"]):
            if not x in self.documents:
                var = IntVar()
                var.trace("w", self.change_callback)
                check = Checkbutton(self.documents_frame, text=x, variable=var)
                check.grid(sticky="W", padx=10)
                self.documents.append(x)
                self.documents_vars.append(var)
                self.additional_documents.append(x)
                self.additional_documents_vars.append(var)
                self.additional_documents_widgets.append(check)

    def del_additional_documents(self):
        self.general_widgets[2].set_completion_list([])
        self.general_widgets[3].set_completion_list([])
        self.general_widgets[7].set_completion_list([])
        self.general_widgets[8].set_completion_list([])
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
        self.general_vars[4].set(date)

    def text_mouseover_callback(self, mouseover):
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
            self.master.bind("<Command-a>", self.archive)
        else:
            self.master.bind("<Control-a>", self.archive)

    def disable_archive(self):
        self.go_button["state"] = "disabled"
        self.file_menu.entryconfigure("Archive", state="disabled")
        if platform.system() == "Darwin":
            self.master.unbind("<Command-a>")
        else:
            self.master.unbind("<Control-a>")

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

        # Check if archving is possible
        try:
            if current_project != "" and \
                            self.general_vars[3].get() != "" and \
                            self.general_vars[4].get()!= "":
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
                    self.config[current_project]["measurements"][t])
            except:
                pass

        # Adapt Protocol according to Measurement Name
        for idx, x in enumerate(self.measurements):
            try:
                t = x[1].get()
                n = x[3].get()
                if t != "anatomical" and n != "":
                    e = "*"

                    prt = "_".join(self.get_filename().split("_")[:-2]) + \
                          "_" + n + e
                    if prt != self.prt_files[idx]:
                        if self.prt_files[idx] == "":
                            start = 1.0
                        elif self.prt_files[idx] != "":
                            start = x[4].search(self.prt_files[idx], 1.0,
                                                stopindex=END)
                            end = ".".join([start.split(".")[0],
                                           repr(len(self.prt_files[idx]))])
                            x[4].delete(start, end)
                        x[4].insert(start, prt)
                        self.prt_files[idx] = prt
            except:
                pass

        if args[0] == str(self.general_vars[0]):
            try:
                self.general_widgets[2].set_completion_list(
                    self.config[current_project]["groups"])
                self.general_widgets[3].set_completion_list(
                    self.config[current_project]["sessions"])
                self.general_widgets[7].set_completion_list(
                    self.config[current_project]["users"])
                self.general_widgets[8].set_completion_list(
                    self.config[current_project]["backups"])
                for index, m in enumerate(self.measurements_widgets):
                    t = self.measurements[index][1].get()
                    m[3].set_completion_list(self.config[current_project]["measurements"][t])
                self.add_additional_documents()
            except:
                self.del_additional_documents()

    def load_config(self):
        """Load the config file."""

        if os.path.exists("sst.cfg"):
            with open("sst.cfg") as f:
                for line in f:
                    if line.startswith("Project:"):
                        project = line[8:].strip()
                        self.config[project] = {"groups": [],
                                                "sessions": [],
                                                "users": [],
                                                "backups": [],
                                                "measurements": {
                                                    "anatomical": [],
                                                    "functional": [],
                                                    "incomplete": []}}
                    elif line.startswith("Groups:"):
                        self.config[project]['groups'] = \
                            [x.strip() for x in line[7:].strip().split(",")]
                        self.config[project]["groups"].sort()
                    elif line.startswith("Sessions:"):
                        self.config[project]["sessions"] = \
                            [x.strip() for x in line[9:].strip().split(",")]
                        self.config[project]["sessions"].sort()
                    elif line.startswith("Users:"):
                        self.config[project]["users"] = \
                            [x.strip() for x in line[6:].strip().split(",")]
                        self.config[project]["users"].sort()
                    elif line.startswith("Backups:"):
                        self.config[project]["backups"] = \
                            [x.strip() for x in line[8:].strip().split(",")]
                        self.config[project]["backups"].sort()
                    elif line.startswith("Measurements Anatomical:"):
                        self.config[project]["measurements"]["anatomical"] = \
                            [x.strip() for x in line[24:].strip().split(",")]
                        self.config[project]["measurements"]["anatomical"].sort()
                    elif line.startswith("Measurements Functional:"):
                        self.config[project]["measurements"]["functional"] = \
                            [x.strip() for x in line[24:].strip().split(",")]
                        self.config[project]["measurements"]["functional"].sort()
                    elif line.startswith("Measurements Incomplete:"):
                        self.config[project]["measurements"]["incomplete"] = \
                            [x.strip() for x in line[24:].strip().split(",")]
                        self.config[project]["measurements"]["incomplete"].sort()
                    elif line.startswith("Documents:"):
                        self.config[project]["documents"] = \
                            [x.strip() for x in line[10:].strip().split(",")]

    def get_filename(self):
        proj = self.general_vars[0].get()
        if proj == "":
            proj = "Project"
        group = self.general_vars[2].get()
        if group != "":
            group = "[{0}]".format(group)
        subj = self.general_vars[1].get()
        if subj == "":
            subj = "Subj"
        else:
            subj = "S" + repr(int(subj)).zfill(2) + group
        sess = self.general_vars[3].get()
        if sess == "":
            sess = "Sess"
        date = self.general_vars[4].get()
        if date == "":
            date = "Date"
        else:
            data = "".join(date.split("-")[::-1])
        filename = "{0}_{1}_{2}_ScanProtocol_{3}".format(proj, subj,
                                                             sess, date)
        return filename

    def save(self, filename=None, *args):
        """Save the data."""

        if type(filename) is  not str:
            filename = self.get_filename()
            f = tkFileDialog.asksaveasfile(mode='w', defaultextension='txt',
                                           initialfile=filename)
        else:
            f = open(filename, 'w')
        if f is None:
            return
        f.write("General Information\n")
        f.write("===================\n")
        f.write("\n")
        for pos, label in enumerate(self.general):
            try:
                value = self.general_vars[pos].get()
            except:
                value = ""
            f.write("{0}{1}{2}\n".format(label, " "*(30-len(label)),
                                         value))
        f.write("\nNotes")
        f.write("\n........")
        try:
            f.write("\n{0}".format(self.general_widgets[-1].get(1.0, END)))
        except:
            pass
        f.write("........\n")
        f.write("\n")
        f.write("\n")
        f.write("\n")
        f.write("Documents\n")
        f.write("=========\n")
        f.write("\n")
        states = ("[ ]", "[x]")
        for pos, label in enumerate(self.documents):
            try:
                value = int(self.documents_vars[pos].get())
            except:
                value = 0
            f.write("{0} {1}\n".format(states[value], label))
        f.write("\n")
        f.write("\n")
        f.write("\n")
        f.write("Measurements\n")
        f.write("============\n")
        for m in self.measurements:
            f.write("\n")
            f.write("No. {0}\n".format(m[0].get()))
            f.write("-----\n\n")
            for elem in range(1, len(self.measurement)-1):
                if elem == 4:
                    try:
                        l = m[elem].get(1.0, END).split("\n")
                        l = [x.strip() for x in l if x != ""]
                        l = [" " * 31 + x if index > 0 \
                                 else x for index, x in enumerate(l)]
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
                    " "*(30-len(self.measurement[elem])),
                    value))
            f.write("\nComments")
            f.write("\n........")
            try:
                f.write("\n{0}".format(m[-1].get(1.0, END)))
            except:
                pass
            f.write("........\n\n")
        f.close()
        self.disable_save()

    def load(self, *args):
        """Load data."""

        f = tkFileDialog.askopenfile("r", filetypes=[("text files", "txt")])
        if f is not None:
            current_document = 0
            measurement = False
            measurement_starts = []
            notes_block = False
            comments_block = False
            if len(self.measurements) == 0:
                self.new_measurement()
            while len(self.measurements) > 1:
                self.del_measurement()
            for linenr, line in enumerate(f):
                if 3 <= linenr <= 11:
                    self.general_vars[linenr-3].set(line[30:].strip())
                    self.del_additional_documents()
                elif not measurement:
                    if not notes_block and line.startswith("........"):
                        notes_block = True
                    elif notes_block:
                        if line.startswith("........"):
                            notes_block = False
                        else:
                            if self.general_widgets[-1].get(1.0, END).strip("\n") == "":
                                self.general_widgets[-1].insert(END,
                                                                line.strip())
                            else:
                                self.general_widgets[-1].insert(END,
                                                                "\n" + line.strip())
                    elif line.startswith("Measurements"):
                        measurement = True
                    else:
                        try:
                            self.add_additional_documents()
                            check = line[1]
                            if check == " ":
                                value = 0
                            elif check == "x":
                                value = 1
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
                            line[4:].strip())
                        measurement_starts.append(linenr)
                    elif linenr >= measurement_starts[-1]+3:
                        if line.startswith("Type:") or\
                                line.startswith("Vols:") or\
                                line.startswith("Name:"):
                            self.measurements[
                                len(measurement_starts)-
                                1][linenr-measurement_starts[-1]-
                                   2].set(line[31:].strip())
                        elif line.startswith("Logfiles:"):
                            widget = self.measurements[
                                len(measurement_starts)-
                                1][-2]
                            widget.delete(1.0, END)
                            widget.insert(END, line[31:].strip())
                        elif line.startswith(" " * 30):
                            widget = self.measurements[
                                len(measurement_starts)-
                                1][-2]
                            widget.insert(END, "\n" + line[31:].strip())
                    if line.startswith("........"):
                        if comments_block is False:
                            comments_block = True
                        else:
                            comments_block = False
                    elif comments_block:
                        if self.measurements[len(measurement_starts)-
                                1][-1].get( 1.0, END).strip("\n") == "":
                            self.measurements[len(measurement_starts)-
                                              1][-1].insert(END,
                                                            line.strip())
                        else:
                            self.measurements[len(measurement_starts)-
                                              1][-1].insert(END,
                                                            "\n" + line.strip())

            self.disable_save()

    def archive(self, *args):
        """Archive the data."""

        d = tkFileDialog.askdirectory(
            title="Select directory containing all data")
        if d is not "":
            self.disable_archive()
            warnings = "\n\n\n"
            project = self.general_vars[0].get()
            group = self.general_vars[1].get()
            subject = int(self.general_vars[2].get())
            session = self.general_vars[3].get()
            timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
            folder = os.path.join(d, "~Archive"+timestamp)
            if not os.path.exists(folder):
                os.makedirs(folder)
            for measurement in self.measurements:
                number = int(measurement[0].get())
                type = measurement[1].get()
                try:
                    vols = int(measurement[2].get())
                except:
                    vols = 0
                name = measurement[3].get()
                scans = []
                for f in glob.glob(os.path.join(d, "*.dcm")):
                    if int(os.path.split(f)[-1].split("_")[1]) == number:
                        scans.append(f)
                if len(scans) == 0:
                    for f in glob.glob(os.path.join(d, "*.IMA")):
                        if int(os.path.split(f)[-1].split(".")[3]) == number:
                            scans.append(f)
                if name == "":
                    warnings += "\nError copying DICOMS for Measurement {0} " \
                               "('Name' not specified)!\n".format(number)
                    continue
                if vols == 0:
                    warnings += "\nError copying DICOMs for Measurement {0} " \
                               "('Vols' not specified)!\n".format(number)
                elif scans == []:
                    warnings += "\nError copying DICOMs for Measurement {0} (" \
                                "No images found)!\n".format(
                        number)
                elif len(scans) != vols:
                    warnings += "\nError copying DICOMs for Measurement {0} ('" \
                                "Vols' unequals number of images)!\n".format(
                        number)
                else:
                    try:
                        project_folder = os.path.join(folder, project)
                        if not os.path.exists(project_folder):
                            os.makedirs(project_folder)
                        group_folder = os.path.join(project_folder, group)
                        if not os.path.exists(group_folder):
                            os.makedirs(group_folder)
                        subject_folder = os.path.join(group_folder,
                                                      "S" + repr(
                                                          subject).zfill(2))
                        if not os.path.exists(subject_folder):
                            os.makedirs(subject_folder)
                        session_folder = os.path.join(subject_folder, session)
                        if not os.path.exists(session_folder):
                            os.makedirs(session_folder)
                        type_folder = os.path.join(session_folder, type[:4])
                        if not os.path.exists(type_folder):
                            os.makedirs(type_folder)
                        name_folder = os.path.join(type_folder, name)
                        if not os.path.exists(name_folder):
                            os.makedirs(name_folder)
                    except:
                        warnings += "\nError creating folder structure for " \
                                    "measurement {0}!\n".format(number)
                        shutil.rmtree(dicom_folder)

                    if os.path.isdir(os.path.join(d, "TBVFiles")):
                        try:
                            # TBV files
                            tbv_folder = os.path.join(name_folder, "TBV")
                            if not os.path.exists(tbv_folder):
                                os.makedirs(tbv_folder)

                            if name == "Anatomy":
                                # Anatomy
                                for file in glob.glob(
                                        os.path.join(d, "TBVFiles/Anatomy/*")):
                                    if not file.endswith("dcm"):
                                        shutil.copy(os.path.abspath(file),
                                                    tbv_folder)
                            else:
                                # Run
                                for file in glob.glob(
                                        os.path.join(d, "TBVFiles/*.tbv")):
                                    f = open(file)
                                    content = f.read()
                                    start = content.find("DicomFirstVolumeNr:")
                                    end = content.find("\n", start)
                                    if int(content[start:end].split(
                                            " ")[-1]) == number:
                                        start = content.find("TargetFolder:")
                                        end = content.find("\n", start)
                                        target_folder = \
                                            content[start:end].split(
                                                " ")[-1].strip("\r").strip('"')
                                        start = content.find("WatchFolder:")
                                        end = content.find("\n", start)
                                        watch_folder = \
                                            content[start:end].split(
                                                " ")[-1].strip("\r").strip('"')
                                        start = content.find("StimulationProtocol:")
                                        end = content.find("\n", start)
                                        stimulation_protocol = \
                                            content[start:end].split(
                                                " ")[-1].strip("\r").strip('"')
                                        start = content.find("ContrastFile:")
                                        end = content.find("\n", start)
                                        contrast_file = \
                                            content[start:end].split(
                                                " ")[-1].strip("\r").strip('"')
                                        start = content.find("FMRVMRAlignVMRPosFile:")
                                        end = content.find("\n", start)
                                        pos_file = \
                                            content[start:end].split(
                                                " ")[-1].strip("\r").strip('"')
                                        start = content.find("ACPCTransformationFile:")
                                        end = content.find("\n", start)
                                        acpc_file = \
                                            content[start:end].split(
                                                " ")[-1].strip("\r").strip('"')
                                        start = content.find("TalairachCerebrumBorderFile:")
                                        end = content.find("\n", start)
                                        tal_file = \
                                            content[start:end].split(
                                                " ")[-1].strip("\r").strip('"')
                                        start = content.find("TalairachVMRFile:")
                                        end = content.find("\n", start)
                                        vmr_file = \
                                            content[start:end].split(
                                                " ")[-1].strip("\r").strip('"')
                                        f.close()

                                        # Copy files
                                        shutil.copy(os.path.abspath(file), tbv_folder)
                                        for elem in os.listdir(
                                            os.path.join(d, "TBVFiles",
                                                         target_folder)):
                                            shutil.copy(
                                                os.path.join(d, "TBVFiles",
                                                             target_folder,
                                                             elem),
                                                             tbv_folder)
                                        if stimulation_protocol != "":
                                            shutil.copy(
                                                os.path.join(d, "TBVFiles",
                                                             stimulation_protocol),
                                                tbv_folder)
                                        if contrast_file != "":
                                            shutil.copy(
                                                os.path.join(d, "TBVFiles",
                                                             contrast_file),
                                                tbv_folder)

                                        # Adapt TBV file
                                        replace(os.path.join(
                                            tbv_folder, os.path.split(file)[-1]),
                                                target_folder, "./")
                                        replace(os.path.join(
                                            tbv_folder, os.path.split(file)[-1]),
                                                watch_folder, "./../DICOM/")
                                        for x in [pos_file, acpc_file, tal_file, vmr_file]:
                                            replace(os.path.join(
                                                tbv_folder, os.path.split(file)[-1]),
                                                    x, os.path.join(
                                                    "../../../anatomical/Anatomy/TBV/",
                                                    os.path.split(x)[-1]))
                            if os.listdir(tbv_folder) == []:
                                shutil.rmtree(tbv_folder)
                        except:
                            warnings += "\nError copying Turbo Brain Voyager files " \
                                        "for Measurement {0}!\n".format(number)
                            shutil.rmtree(tbv_folder)

                    try:
                        # DICOMs
                        dicom_folder = os.path.join(name_folder, "DICOM")
                        if not os.path.exists(dicom_folder):
                            os.makedirs(dicom_folder)
                        for s in scans:
                            shutil.copyfile(
                                s, os.path.join(folder, project, group,
                                                "S" + repr(subject).zfill(2),
                                                session, type[:4], name, "DICOM",
                                                os.path.split(s)[-1]))
                    except:
                        warnings += "\nError copying DICOMs for Measurement " \
                                    "{0} (filesystem error)!\n".format(number)
                        shutil.rmtree(dicom_folder)

                # Logfiles
                if type != "anatomical":
                    try:
                        original = measurement[4].get(1.0, END)
                        logfiles = original.split("\n")
                        logfiles = [x.strip() for x in logfiles if x != ""]
                        for logfile in logfiles:
                            if "*" in logfile:
                                replaced = []
                            try:
                                if logfile != "" and not os.path.isdir(logfile):
                                    files = glob.glob(os.path.join(d,
                                                                   logfile))
                                    if files == []:
                                        raise Exception
                                    for file_ in files:
                                        if not os.path.isdir(file_):
                                            if "*" in logfile:
                                                replaced.append(
                                                    os.path.split(file_)[-1])
                                            shutil.copyfile(
                                                file_,
                                                os.path.join(folder,
                                                             project,
                                                             group,
                                                             "S" + repr(
                                                                 subject).zfill(
                                                                 2),
                                                             session, type[:4], name,
                                                             os.path.split(file_)[-1]))
                                    if "*" in logfile:
                                        new = original.replace(
                                            logfile, "\n".join(replaced))
                                        measurement[4].delete(1.0, END)
                                        measurement[4].insert(1.0, new)

                            except:
                               warnings += "\nError copying Logfiles " \
                                   "for Measurement {0} ('{1}' not " \
                                   "found)!\n".format(number, logfile)

                    except:
                        warnings += "\nError copying Logfiles " \
                                   "for Measurement {0}!\n".format(number)

            message = "Data archiving is finished!"

            # Try general TBV files
            if os.path.isdir(os.path.join(d, "TBVFiles")):
                try:
                    func_folder = os.path.join(folder, project, group,
                                               "S" + repr(subject).zfill(2),
                                               session, "functional")
                    for file in glob.glob(os.path.join(d, "TBVFiles/*")):
                        if file.endswith("roi") or file.endswith("voi"):
                            shutil.copy(os.path.abspath(file), func_folder)
                except:
                    warnings += "\nError copying general Turbo Brain Voyager files!\n"
            else:
                warnings += "\nNo Turbo Brain Voyager files found!\n"

            # Try general documents
            try:
                all_documents = 0
                sess_folder = os.path.join(folder, project, group,
                                           "S" + repr(subject).zfill(2),
                                           session)
                for file in glob.glob(os.path.join(d, "*")):
                    if file.endswith("pdf") or file.endswith("doc") \
                        or file.endswith("txt") and not os.path.isdir(file):
                        all_documents += 1
                        shutil.copy(os.path.abspath(file), sess_folder)
                if all_documents == 0:
                    warnings += "\nNo general documents found!"
            except:
                warnings += "\nError copying general documents!"

            # Save scan protocol
            path = os.path.join(folder, project, self.get_filename() + ".txt")
            self.save(path)

            # Confirm archiving
            message += warnings
            tkMessageBox.showinfo(title="Done", message=message)


class HelpDialogue:

    def __init__(self, master):
        self.master = master
        top = self.top = Toplevel(master)
        top.title("Help")
        self.text = ScrolledText(top, width=77)
        self.text.pack()
        try:
            with open("README.txt") as f:
                docs = f.read()
        except:
            docs = "README.txt not found!"
        self.text.insert(END, docs)
        self.text["state"] = "disabled"

        b = Button(top, text="OK", command=self.ok)
        b.pack(pady=5)

    def ok(self):
        self.top.destroy()

    def show(self):
        self.master.wait_window(self.top)


root = Tk()
style = Style()
style.theme_use("default")
root.resizable(False, False)
root.option_add('*tearOff', FALSE)
app = App(master=root)
app.master.title('Scan Session Tool {0}'.format(__version__))
if platform.system() == "Darwin":
    root.bind('<Command-q>', app.quit_callback)
root.bind('<Escape>', lambda x: app.master.focus())
app.bind('<Button-1>', lambda x: app.master.focus())
for label in app.nofocus_widgets:
    label.bind('<Button-1>', lambda x: app.master.focus())
root.protocol("WM_DELETE_WINDOW", app.quit_callback)
app.general_widgets[0].focus()
app.disable_save()
app.mainloop()