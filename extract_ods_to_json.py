"""

takes an input ODS file (open office), converts it to a json file as a list of dictionaries for the rows

all sheets are merged together as one list, but keys may be different between different sheets


for example sheet:

name,       surname,    balance
Richard,    Brown,      12100
Ted,        Johnson,    8122
Gordon,     Smith,      122

=>

[
{'name': "Richard", 'surname': Brown, 'balance': 12100},
{'name': "Ted", 'surname': Johnson, 'balance': 8122},
{'name': "Gordon", 'surname': Smith, 'balance': 122}
]

note, numbers may become strings, it's best to be careful of numbers


https://pypi.org/project/pyexcel-ods3/

pip install pyexcel-ods3


shell command:
python ods_to_json.py <filename>


"""
from pyexcel_ods3 import get_data
import json
import sys
import os


filename = sys.argv[1] # filename as the first par passed

print("attempt to convert filename: \"{}\"".format(filename))

assert(os.path.exists(filename))


# converts all the sheets of a ods into json using the convention that the first row is the keys
# the next rows if they have anything in them is the data
# the json is a giant list of entries
def convert_ods_to_json(filename, out_filename=None):

    data = get_data(filename)

    items = []

    items_dict = {} ## feature 2

    print("load file: \"{}\"".format(filename))

    for sheet_name in data:

        print("found sheet: \"{}\"".format(sheet_name))

        sheet = data[sheet_name]

        keys = None

        for row in sheet:

            item = {}

            if not keys:  # first row as keys
                keys = row
            else:

                if len(row) > 0:
                    items.append(item)

                    for i in range(len(row)):
                        val = row[i]
                        key = keys[i]
                        item[key] = val

                    _id = row[0]
                    items_dict[_id] = item




    if not out_filename:
        out_filename = "{}.json".format(filename)

    print("save file to: \"{}\"".format(out_filename))

    # Write pretty print JSON data to file
    with open(out_filename, "w") as write_file:
        json.dump(items, write_file, indent=4)


    out_filename2 = None
    if not out_filename2:
        out_filename2 = "{}.keys.json".format(filename)
    with open(out_filename2, "w") as write_file:
        json.dump(items_dict, write_file, indent=4)


convert_ods_to_json(filename)
