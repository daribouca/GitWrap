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
import shutil_rmtree

import exe_wrapper
import git_exceptions

def random_string(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

def make_random_file(in_folder):
    if not os.path.exists(in_folder):
        os.makedirs(in_folder)
    file_name = random_string(chars="ABCDEFGH")
    file_path = os.path.join(in_folder, file_name)
    with open(file_path, mode="w") as f:
        f.write(random_string(size=64))
    return os.path.abspath(file_path)

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

    def tearDown(self):
        remove(self.main_dir)
        pass

    def test_set_wk_dir(self):
        d = os.path.join(self.main_dir, "test_set_wk_dir")
        t = exe_wrapper.GitWrapper(d)
        t._set_wkdir(self.main_dir)
        with self.assertRaises(git_exceptions.GitWrapperException):
            t._set_wkdir("this_path_does_not_exist")

    def test_set_timeout(self):
        d = os.path.join(self.main_dir, "test_set_timeout")
        t = exe_wrapper.GitWrapper(d)
        t.set_timeout(1)
        t.set_timeout(120)
        for x in ["str", 0, 121, 1000]:
            with self.assertRaises(git_exceptions.GitWrapperException):
                t.set_timeout(x)

    def test_set_cmd(self):
        d = os.path.join(self.main_dir, "test_set_cmd")
        t = exe_wrapper.GitWrapper(d)
        t._set_cmd(["test"])
        t._set_cmd(["test","test","test"])
        for x in [["test",1,"test"], ["test",None,"test"], ["test",False,"test"], ["test",exe_wrapper,"test"]]:
            with self.assertRaises(git_exceptions.GitWrapperException):
                t._set_cmd(x)

    def test_init(self):
        d = os.path.join(self.main_dir, "test_init")
        t = exe_wrapper.GitWrapper(d)
        t.init()
        t = exe_wrapper.GitWrapper(d, git_exe="C:/Documents and Settings/owner/My Documents/BORIS/live/git-portable/bin/git.exe")
        with self.assertRaises(git_exceptions.GitWrapperException):
            exe_wrapper.GitWrapper(d, git_exe="this path does not exist")
        f = make_random_file(d)
        with self.assertRaises(git_exceptions.GitWrapperException):
            t = exe_wrapper.GitWrapper(f)
            t.init()
        d = os.path.join(self.main_dir, "test_init_bare")
        t = exe_wrapper.GitWrapper(d)
        t.init(bare=True)

    def test_init_bare(self):
        d = os.path.join(self.main_dir, "test_init_bare")

    def test_init_existing(self):
        d = os.path.join(self.main_dir, "test_init_existing")

    def test_init_bare_existing(self):
        d = os.path.join(self.main_dir, "test_init_bare_existing")

    def test_init_existing_non_empty(self):
        d = os.path.join(self.main_dir, "test_init_existing_non_empty")
        return
        os.makedirs(d)
        with open(os.path.join(d, "test_file"), mode="w") as f:
            f.write("test")
        exe_wrapper.init(d)

    def test_init_bare_existing_non_empty(self):
        d = os.path.join(self.main_dir, "test_init_bare_existing_non_empty")
        return
        os.makedirs(d)
        with open(os.path.join(d, "test_file"), mode="w") as f:
            f.write("test")
        with self.assertRaises(exe_wrapper.GitWrapperException):
            exe_wrapper.init(d, bare=True)

def remove(d):
    shutil.rmtree(d, onerror=shutil_rmtree.onerror)

if __name__ == '__main__':
    unittest.main()

