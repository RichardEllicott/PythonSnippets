"""

opening the file in the system's gui, like a text/html file for example

only works on mac

"""

from __future__ import absolute_import, division, print_function # makes code Python 2 and 3 compatible mostly

import os


def open_in_system(filename)
    os.system("open {}".format(filename))  # mac open command, would open for example a text document in a text editor
