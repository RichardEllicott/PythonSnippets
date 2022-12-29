"""

simple TKInter button menu to launch commands


just adding buttons with commands, good for a launch menu like a doom wad launcher


"""

from __future__ import absolute_import, division, print_function
import Tkinter as tk

class SimpleTKMenu():
    """
    a simple menu with simply buttons
    """

    profile = [
        ["buttonA", lambda: print("pressed buttonA!")], # first entry is label, second is command (function or lambda)
        ["buttonB", lambda: print("pressed buttonB!")],
    ]

    number_rows = False  # label the row numbers

    def __init__(self):

        row = 0
        for entry in self.profile:
            column = 0
            if self.number_rows:
                tk.Label(text=row).grid(row=row, column=column)
                column += 1

            tk.Button(text=entry[0], relief=tk.RIDGE, width=30, command=entry[1]).grid(row=row, column=column)
            column += 1

            row += 1

        tk.mainloop()

        pass

    pass


tkmen = SimpleTKMenu()