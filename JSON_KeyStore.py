"""
simple JSON keyed database

now behaves like a dictionary (sort of)

more expensive than a database as it has to read/write entire file, usually every time a key is changed (unless autocommit is False)


"""
import os
import json


# https://stackoverflow.com/questions/2060972/subclassing-python-dictionary-to-override-setitem
# seems to be the lightest way to override a dict

class KeyStore(dict):
    """
    behaves as a dict, saves itself as JSON file

    inherits from dict, this is deliberate, the alternatives involve too much re-implementation

    works for:
        -set
        -update
        -clear
    """

    changes_made = False  # if true, pending changes to be written to file

    def __init__(self, filename, autocommit=False):
        self.filename = filename
        self.autocommit = autocommit

        if os.path.exists(filename):
            with open(self.filename) as file:
                data = json.load(file)

                # self.update(data)
                super(KeyStore, self).update(data)  # avoid our trigger

    def commit(self):
        """save to file if any changes have been made
        """

        if self.changes_made:
            self.changes_made = False

            # print("COMMIT: ", self)

            with open(self.filename, 'w') as file:
                file.write(json.dumps(self, indent=4))

    def _on_edit(self):
        """triggered on any changes to dict
        """

        self.changes_made = True
        if self.autocommit:
            self.commit()

    def __del__(self):
        """when object is garbage collected, ensure a final commit is made

        ISSUE:
        NameError: name 'open' is not defined
        CAUSE:
        in some cases open is destroyed before this object, in which case "commit" before end of program
        """
        self.commit()

    def __setitem__(self, key, value):
        """override __setitem__ adds our _on_edit trigger
        """
        super(KeyStore, self).__setitem__(key, value)
        self._on_edit()

    def update(self, _dict):
        """
        when we use update must cause trigger

        issue when using *args, so can only add one dict at a time... i think workaround is here:
        https://stackoverflow.com/questions/2060972/subclassing-python-dictionary-to-override-setitem

        but decided to restrict to one par

        """
        super(KeyStore, self).update(_dict)
        self._on_edit()

    def clear(self):
        super(KeyStore, self).clear()
        self._on_edit()

    # this avoids bugs documented apparently in:
    # https://stackoverflow.com/questions/2060972/subclassing-python-dictionary-to-override-setitem

    def setdefault(self, key, value=None):
        """not sure what is used for yet
        """
        if key not in self:
            self[key] = value
        return self[key]


def test():

    filename = "JSON_KeyStore.test.tmp.json"

    json_dict = KeyStore(filename, autocommit=False)

    print(json_dict)


    # json_dict.clear()

    # json_dict['apple'] = 4
    # json_dict['pear'] = 2
    json_dict['orange'] = 6

    # json_dict.update({'rose': 'a string', 'stuff': [1,2,3,4]})

    print(json_dict)


if __name__ == "__main__":
    print("run unit tests...")

    test()


print("FIN!!!")
