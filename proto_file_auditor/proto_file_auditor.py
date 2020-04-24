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

from send2trash import send2trash

from glob import glob
import os
import re
import hashlib
import time

import json
import pickle


AUDIT_FOLDER = "./"


SCAN_CACHE_FILENAME = "proto_file_auditor.TEMP"


def write_to_json(filename, data):
    with open(filename, 'wb') as f:
        data = json.dumps(data, indent=4,ensure_ascii=False) # writes unicode in the ascii
        # data = json.dumps(data, indent=4) # SHOW NOT WORKIN FOR SPECIAL CHARS
        f.write(data)



def write_to_pickle(filename, data):
    pickle.dump( data, open( filename, 'wb' ) )


def read_from_pickle(filename):
    return pickle.load( open( filename, "rb" ) )


        
import io


def read_from_json(filename):
    with open(filename, 'r') as f:
        data = json.loads(f.read())
        # data = json.loads(f.read().decode('string-escape').decode("utf-8"))


        # return data

        # return json_load_byteifiedteified(f)

    # with io.open(filename, mode="r", encoding="utf-8") as f:
    #     data = json.loads(f.read().encode('utf-8'))
    #     return data


# solution for loading to str not unicode
# https://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-from-json

def json_load_byteified(file_handle):
    return _byteify(
        json.load(file_handle, object_hook=_byteify),
        ignore_dicts=True
    )

def json_loads_byteified(json_text):
    return _byteify(
        json.loads(json_text, object_hook=_byteify),
        ignore_dicts=True
    )

def _byteify(data, ignore_dicts = False):
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [ _byteify(item, ignore_dicts=True) for item in data ]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in data.iteritems()
        }
    # if it's anything else, return it in its original form
    return data


def get_file_md5(filename):
    with open(filename, 'r') as f:
        chunk_size = 1024
        hasher = hashlib.md5()
        while True:
            try:
                data = f.read(chunk_size)
            except IOError, e:
                log.error('error hashing %s on Agent %s' % (path, agent.name))
                return {'error': '%s' % e}
            if not data:
                break
            hasher.update(data)
        return hasher.hexdigest()


class AuditTexturesFolderSession():

    hash_files = True

    target_folder = AUDIT_FOLDER

    dirnames = []

    filenames = []

    data = {}  # []

    file_details = None  # = {}

    def get_debug_string(self, ttl=-1):
        s = ""
        s += "[AUDIT DATA BEGIN]\n"

        for entry in self.data:
            if ttl == 0:
                s += "<WARNING, DATA TRUNCATED!>\n"
                break
            data = self.data[entry]
            s += "{} {}\n".format(entry, data)

            ttl -= 1

        s += "total count: {}\n".format(len(self.data))

        s += "[AUDIT DATA END]\n"

        return s

    def save_data(self):
        write_to_json(SCAN_CACHE_FILENAME + ".json", self.data)
        write_to_pickle(SCAN_CACHE_FILENAME + ".pickle", self.data)

        with open(SCAN_CACHE_FILENAME + ".filenames.txt", 'wb') as f:
            for filename in self.filenames:
                f.write(filename + "\n")

        with open(SCAN_CACHE_FILENAME + ".interlaced.txt", 'wb') as f:
            for filename in self.data:
                data = self.data[filename]
                f.write("{}\n{}\n{}\n".format(filename,data['modified'],data['md5']))

    def load_data(self):

        self.data = read_from_json(SCAN_CACHE_FILENAME + ".json")



        pass

    def __init__(self, target_folder):
        print(self, " init... ")

        self.dirnames = []

        self.target_folder = target_folder

        self.data = {}

        self.walk_folders(self.target_folder)

        self.save_data()


    def walk_folders(self, pattern="."):

        ttl = 10  # for debug (-1 if infinite)

        for root, dirs, files in os.walk(pattern, topdown=False):
            for name in files:

                if ttl == 0:
                    break
                # print(os.path.join(root, name))
                path = os.path.join(root, name)
                mod_time = os.path.getmtime(path)

                data = {}
                data['modified'] = mod_time
                data['path'] = path
                data['size'] = os.path.getsize(path)


                md5 = ""

                if self.hash_files:
                     md5 = get_file_md5(path)
                data['md5'] = md5

                data['null_test'] = None

                self.data[path] = data

                self.filenames.append(path)

                ttl -= 1

            for name in dirs:
                # print("FOLDDLDL:", os.path.join(root, name))
                self.dirnames.append(os.path.join(root, name))
                # print(os.path.getmtime(path))
                pass


session = AuditTexturesFolderSession(AUDIT_FOLDER)
print(session.get_debug_string())

# print(session.data)


    







