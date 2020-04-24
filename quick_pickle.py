"""



"""

from __future__ import absolute_import, division, print_function  # makes code Python 2 and 3 compatible mostly


import pickle



def save_pickle(filename, data):
    pickle.dump( data, open( filename, 'wb' ) )


def load_pickle(filename):
    return pickle.load( open( filename, "rb" ) )


data = {22: 78, 827: 234, "hello": 23}
test_filename = "pickle_test.temp"
save_pickle(test_filename,data)
print(load_pickle(test_filename))