"""



"""

from __future__ import absolute_import, division, print_function  # makes code Python 2 and 3 compatible mostly

import json


def write_to_json(filename, data):
    with open(filename, 'w+') as f:
        data = json.dumps(data, indent=4) # writes pretty
        f.write(data)


def read_from_json(filename):
    with open(filename, 'r') as f:
        data = json.loads(f.read())
        return data


write_to_json("test.json", {"hello": 77, "bob": 22})  # example
print(read_from_json("test.json"))
