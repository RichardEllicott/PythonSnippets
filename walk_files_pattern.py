"""

alternative to using a glob pattern, can get folders also

"""


from __future__ import absolute_import, division, print_function

import os

def walk_folders(pattern = "."):

        filenames = []
        foldernames = []

        for root, dirs, files in os.walk(pattern, topdown=False):
            for name in files:
                path = os.path.join(root, name)
                print("found file: ",path, " | ", name)
                filenames.append(path)

            for name in dirs:
                path = os.path.join(root, name)
                print("found folder: ",path, " | ", name)
                foldernames.append(path)


        return (filenames, foldernames)


# print(walk_folders())



def scan_folder(self, pattern="." , ttl = -1):

    files_dict = {}
    folder_dict = {}

    hash_files = True

    for root, dirs, files in os.walk(pattern, topdown=False):
        for name in files:
            if ttl == 0:
                break
            path = os.path.join(root, name)
            mod_time = os.path.getmtime(path)

            data = {}
            data['modified'] = mod_time
            data['path'] = path
            data['size'] = os.path.getsize(path)
            data['type'] = "file"

            data['null_test'] = None

            files_dict[path] = data


            ttl -= 1

        for name in dirs:
            # print("FOLDDLDL:", os.path.join(root, name))
            # self.dirnames.append(os.path.join(root, name))
            # print(os.path.getmtime(path))
            pass

    return files_dict




scan_results = scan_folder(".")
for result in scan_results:
    print(result, scan_results[result])








