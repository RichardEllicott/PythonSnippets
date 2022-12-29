"""

quick csv functions

latin1 is a bit of a hack but i can never seem to get python to accept unicode anyway

"""


import glob



def load_csv(filename):
    ret = []
    with open(filename, newline='', encoding='latin1') as f: # latin1 workaround?
        reader = csv.reader(f)
        for row in reader:
            ret.append(row)
    return ret


def load_csv_table(filename):
    """
    load a special table where the top row is keys
    adds all filled values to the records (but ignores blank entries)
    """
    keys = []
    ret = []
    with open(filename, newline='', encoding='latin1') as f: # latin1 workaround?
        reader = csv.reader(f)
        n = 0
        for row in reader:
            if n == 0:
                keys = row
            else:
                record = {}
                for i in range(len(keys)):
                    key = keys[i]
                    val = row[i]
                    if val != "": # eliminates empty records allowing spacing in the spreadsheet
                        record[key] = val
                if len(record) > 0:
                    ret.append(record)
            n += 1
    return ret



## added 03/03/2022
def load_csv(filename):
    with open(filename) as f:
        reader = csv.reader(f)
        return list(reader)
