
import os

path = "{}\\".format(os.getcwd())

path = "C:\\Users\\Richard\\Desktop"

print("path:", path)

def fast_scandir(dirname):
    subfolders= [f.path for f in os.scandir(dirname) if f.is_dir()]
    for dirname in list(subfolders):
        subfolders.extend(fast_scandir(dirname))
    return subfolders


for result in fast_scandir(path):
	print(result)