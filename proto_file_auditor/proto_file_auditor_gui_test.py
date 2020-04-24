"""

proto_file_auditor.py

prototype backup system, designed to track backups to a USB key etc

(made for when backing up to github is annoying because of lots of data etc)



using Send2Trash for sending to mac trash
sudo pip install --user Send2Trash



fave textures:

Soil3_3x3 # for desert
Brick_Rustic # big medieval blocks
Concrete_BrickWall # straight large blocks



print(os.path.getmtime(test_path)) # last modified time





DEV NOTES:

neither pickle or json work well with unicode chars, but plain text seems okay

"""


from __future__ import absolute_import, division, print_function
import Tkinter as tk

class SimpleTKMenu():

    profile = [
        ["buttonA", lambda: print("pressed buttonA")],
        ["buttonB", lambda: print("pressed buttonB")],
    ]

    number_rows = False  # label the row numbers

    def __init__(self):

        r = 0
        for entry in self.profile:
            c = 0
            if self.number_rows:
                tk.Label(text=r).grid(row=r, column=c)
                c += 1

            tk.Button(text=entry[0], relief=tk.RIDGE, width=30, command=entry[1]).grid(row=r, column=c)
            c += 1

            r += 1

        tk.mainloop()

        pass

    pass


tkmen = SimpleTKMenu()
