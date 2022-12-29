"""

PYTHON 3 VERSION, works with unicode!




proto_file_auditor2.py

prototype backup system, designed to track backups to a USB key etc

(made for when backing up to github is annoying because of lots of data etc)


using Send2Trash for sending to mac trash
sudo pip install --user Send2Trash





print(os.path.getmtime(test_path)) # last modified time





DEV NOTES:

neither pickle or json work well with unicode chars, but plain text seems okay

"""


# from send2trash import send2trash


from glob import glob
import os
import re
import hashlib
import time

import json
import pickle
import io


AUDIT_FOLDER = "./"
# AUDIT_FOLDER = "/Users/rich/GodotLocal"


SCAN_CACHE_FILENAME = "proto_file_auditor.TEMP"


def write_to_json(filename, data):
    with open(filename, 'wb') as f:
        data = json.dumps(data, indent=4, ensure_ascii=False)  # writes unicode in the ascii
        f.write(bytes(data, 'utf-8'))


def read_from_json(filename):
    with open(filename, 'r') as f:
        return json.loads(f.read())



def get_file_md5(filename):
    with open(filename, 'rb') as f:
        chunk_size = 1024
        hasher = hashlib.md5()
        while True:
            try:
                data = f.read(chunk_size)
            except IOError as e:
                log.error('error hashing %s on Agent %s' % (path, agent.name))
                return {'error': '%s' % e}
            if not data:
                break
            hasher.update(data)
        return hasher.hexdigest()


class AuditTexturesFolderSession():

    hash_files = False

    target_folder = AUDIT_FOLDER


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
        savedict = {}
        savedict['timestamp'] = time.time()
        savedict['data'] = self.data
        write_to_json(SCAN_CACHE_FILENAME + ".json", savedict)
        

    def load_data(self):
        savedict = read_from_json(SCAN_CACHE_FILENAME + ".json")

        self.data = savedict['data']


    def __init__(self, target_folder):
        print(self, " init... ")


        self.target_folder = target_folder

        self.data = {}

        self.walk_folders(self.target_folder)

        self.save_data()

        # self.load_data()

    def walk_folders(self, pattern=".", ttl=-1):

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
                data['type'] = "file"

                md5 = ""
                if self.hash_files:
                    md5 = get_file_md5(path)
                data['md5'] = md5

                self.data[path] = data

                ttl -= 1

            for name in dirs:

                path = os.path.join(root, name)
                mod_time = os.path.getmtime(path)

                data = {}
                data['modified'] = mod_time
                data['path'] = path
                data['size'] = os.path.getsize(path)
                data['type'] = "directory"
                md5 = ""
                data['md5'] = md5

                self.data[path] = data




session = AuditTexturesFolderSession(AUDIT_FOLDER)
print(session.get_debug_string())

# print(session.data)
