"""

prototype backup system, designed to track backups to a USB key etc

(made for when backing up to github is annoying because of lots of data etc)



using Send2Trash for sending to mac trash
sudo pip install --user Send2Trash



fave textures:

Soil3_3x3 # for desert
Brick_Rustic # big medieval blocks
Concrete_BrickWall # straight large blocks



print(os.path.getmtime(test_path)) # last modified time



"""


from __future__ import absolute_import, division, print_function

from send2trash import send2trash

from glob import glob
import os
import re
import hashlib
import time

import json



AUDIT_FOLDER = "/Volumes/64GB/www.textures.com/"



def write_to_json(filename, data):
    with open(filename, 'w+') as f:
        data = json.dumps(data)
        f.write(data)

def read_from_json(filename):
    with open(filename, 'r') as f:
        data = json.loads(f.read())
        return data





def get_file_md5(filename):
    with open(filename,'r') as f:
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

    filenames = []  # = set()
    dirnames = []  # = set()
    filenames_mod_time = []


    file_details = None # = {}


    def get_debug_string(self, ttl = 5):
        s = ""
        s += "***AuditTexturesSession***\n"

        for i in range(len(self.filenames)):
            filename = self.filenames[i]
            mod_time = self.filenames_mod_time[i]

            s += "{} {}\n".format(filename, str(mod_time))
            ttl -= 1
            if ttl <= 0:
                s += "...\n"
                break
        return s


    def __init__(self, *args):
        print(self, " init... ")

        self.filenames = []
        self.filenames_mod_time = []

        self.dirnames = []

        for arg in args:
            self.walk_folders(arg)


    def walk_folders(self, pattern = "."):
        for root, dirs, files in os.walk(pattern, topdown=False):
            for name in files:
                # print(os.path.join(root, name))
                path = os.path.join(root, name)
                self.filenames.append(path)
                self.filenames_mod_time.append(os.path.getmtime(path))
            for name in dirs:
                # print(os.path.join(root, name))
                self.dirnames.append(os.path.join(root, name))



session = AuditTexturesFolderSession(AUDIT_FOLDER)
print(session.get_debug_string())


test_path = "/Volumes/64GB/www.textures.com/TexturesCom_Asphalt3_2x2_1K_normal.png"



def md5_sha_test():

    print("START MD5 SHA TESTS")

    start_time = time.time()

    for i in range(100):
        # print(get_file_md5(test_path)) # 10.2270171642
        # print(get_file_md5_and_sha1(test_path)) # 23.4171528816
        print(get_file_sha1(test_path)) # 14.0846300125

    time_took = time.time() - start_time


    print("time took ", time_took)

# md5_sha_test()





