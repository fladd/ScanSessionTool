"""Widgets.

A set of custom Tkinter widgets used in Scan Session Tool.

"""


import os
import sys
import glob
import shutil
import platform

from tkinter import *
from tkinter.ttk import *


class FixedSizeFrame(Frame):
    """A Tkinter frame with a fixed size."""

    def __init__(self, master, width, height, **kw):
        Frame.__init__(self, master, **kw)
        self["width"] = width
        self["height"] = height
        self.grid_propagate(False)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)


class AutoScrollbarText(Text):
    """A Tkinter text widget with an automatically showing/hiding scrollbar."""

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
                            logfile, "\n".join(sorted(replaced)))
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
        self.bind_ids = []
        if platform.system() == "Linux":
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
    """A Tkinter combobox widget with an autocompletion feature."""

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
    """A Tkinter spinbox with a text entry feature."""

    def __init__(self, master=None, **kw):
        s = Style()
        Entry.__init__(self, master, "ttk::spinbox", **kw)

    def current(self, newindex=None):
        return self.tk.call(self._w, 'current', newindex)

    def set(self, value):
        return self.tk.call(self._w, 'set', value)



