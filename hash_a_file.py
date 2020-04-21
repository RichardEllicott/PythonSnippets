

from __future__ import absolute_import, division, print_function # makes code Python 2 and 3 compatible mostly


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
        return hasher


def get_file_sha1(filename):
    with open(filename,'r') as f:
        chunk_size = 1024
        hasher = hashlib.sha1()
        while True:
            try:
                data = f.read(chunk_size)
            except IOError, e:
                log.error('error hashing %s on Agent %s' % (path, agent.name))
                return {'error': '%s' % e}
            if not data:
                break
            hasher.update(data)
        return hasher

def get_file_md5_and_sha1(filename):
    with open(filename,'r') as f:
        chunk_size = 1024
        hasher = hashlib.md5()
        hasher_sha = hashlib.sha1()
        while True:
            try:
                data = f.read(chunk_size)
            except IOError, e:
                log.error('error hashing %s on Agent %s' % (path, agent.name))
                return {'error': '%s' % e}
            if not data:
                break
            hasher.update(data)
            hasher_sha.update(data)

        return (hasher.hexdigest(), hasher_sha.hexdigest())