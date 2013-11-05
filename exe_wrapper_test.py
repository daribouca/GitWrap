#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      owner
#
# Created:     29/10/2013
# Copyright:   (c) owner 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import sys, os
sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path

import unittest
import string
import random
import shutil
import hashlib

import exe_wrapper

def random_string(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

def make_random_file(in_folder):
    if not os.path.exists(in_folder):
        os.makedirs(in_folder)
    file_name = random_string(chars="ABCDEFGH")
    file_path = os.path.join(in_folder, file_name)
    with open(file_path, mode="w") as f:
        f.write(random_string(size=64))
    return file_path

def file_hash(f, blocksize=65536):
    hasher = hashlib.sha1()
    with open(f, 'rb') as afile:
        buf = afile.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(blocksize)
    return hasher.hexdigest()

class TestExeWrapper(unittest.TestCase):

    main_dir = "./tests/exe_wrapper"
    files = []
    repos = ["./tests/exe_wrapper/repo{}".format(f) for f in range(10)]

    def setUp(self):
        if not os.path.exists(self.main_dir):
            os.makedirs(self.main_dir)
        for x in range(10):
            f_name = "file{}".format(x)
            self.__dict__[f_name] = file_name = os.path.join(self.main_dir, random_string(6, "ABCDEF"))
            with open(self.__dict__[f_name], mode="w") as f:
                f.write(random_string(64))
            self.__dict__["{}_SHA".format(f_name)] = file_SHA = file_hash(self.__dict__[f_name])
            self.files.append([file_name, file_SHA])
        for r in self.repos:
            os.makedirs(r)

    def tearDown(self):
        remove(self.main_dir)
        pass

    def test_init(self):
        d = os.path.join(self.main_dir, "test_init")
        exe_wrapper.init(d)

    def test_init_bare(self):
        d = os.path.join(self.main_dir, "test_init_bare")
        exe_wrapper.init(d, bare = True)

    def test_init_existing(self):
        d = os.path.join(self.main_dir, "test_init_existing")
        os.makedirs(d)
        exe_wrapper.init(d)

    def test_init_bare_existing(self):
        d = os.path.join(self.main_dir, "test_init_bare_existing")
        os.makedirs(d)
        exe_wrapper.init(d, bare=True)

    def test_init_existing_non_empty(self):
        d = os.path.join(self.main_dir, "test_init_existing_non_empty")
        os.makedirs(d)
        with open(os.path.join(d, "test_file"), mode="w") as f:
            f.write("test")
        exe_wrapper.init(d)

    def test_init_bare_existing_non_empty(self):
        d = os.path.join(self.main_dir, "test_init_bare_existing_non_empty")
        os.makedirs(d)
        with open(os.path.join(d, "test_file"), mode="w") as f:
            f.write("test")
        with self.assertRaises(exe_wrapper.GitWrapperException):
            exe_wrapper.init(d, bare=True)

def remove(d):
    shutil.rmtree(d, onerror=exe_wrapper.onerror)

if __name__ == '__main__':
    unittest.main()

