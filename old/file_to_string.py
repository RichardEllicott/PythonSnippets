

from __future__ import absolute_import, division, print_function # makes code Python 2 and 3 compatible mostly



def string_to_file(filename, s):
    with open(filename, 'wb') as f:
        f.write(s)

def file_to_string(filename):
    with open (filename, 'rb') as f:
        return f.read()


test_filename = "file_to_string.test.txt"
string_to_file(test_filename,"hello world!!!")
print(file_to_string(test_filename))
# print(u"hello world...  \xe2\x99\xa1 \xe2\x99\xa5 \xe2\x9d\xa4")


print (u'\u212B\u00B3   \xe2\x99\xa1 \xe2\x99\xa5 \xe2\x9d\xa4'.encode('utf-8'))