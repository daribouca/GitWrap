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
import posixpath
import glob

import exe_wrapper
import git_exceptions

def random_string(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

def make_random_file(in_folder):
    if not os.path.exists(in_folder):
        os.makedirs(in_folder)
    file_name = "F_{}".format(random_string(chars="ABCDEFGH"))
    file_path = os.path.join(in_folder, file_name)
    if os.path.exists(file_path):
        return make_random_file(in_folder)
    with open(file_path, mode="w") as f:
        f.write(random_string(size=64))
    return os.path.abspath(file_path)

def make_random_dir(in_folder):
    folder_path = os.path.join(in_folder, "D_{}".format(random_string(chars="ABCDEFGH")))
    if os.path.exists(folder_path):
        return make_random_dir(in_folder)
    os.makedirs(folder_path)
    return os.path.abspath(folder_path)

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

    def setUp(self):
        if not os.path.exists(self.main_dir):
            os.makedirs(self.main_dir)
        else:
            remove(self.main_dir)
        make_random_file(self.main_dir)

    def tearDown(self):
        remove(self.main_dir)

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
        with self.assertRaises(exe_wrapper.GitWrapperException):
            subd = make_random_dir(d)
            make_random_file(subd)
            t = exe_wrapper.GitWrapper(subd, must_be_empty=True)

    def test_status(self):
        d = os.path.join(self.main_dir, "test_status")
        t = exe_wrapper.GitWrapper(d)
        with self.assertRaises(git_exceptions.GitWrapperException):
            t.status()
        t.init()
        t.status()

##    def test_commit(self):
##        d = os.path.join(self.main_dir, "test_commit")
##        for x in range(10):
##            make_random_file(d)
##        t = exe_wrapper.GitWrapper(d)
##        with self.assertRaises(git_exceptions.GitWrapperException):
##            t.init().commit()
##        t.init(add_all=True).commit()

    def test_clone(self):
        d = os.path.join(self.main_dir, "test_clone")
        d1 = make_random_dir(d)
        d2 = make_random_dir(d)
        d3 = make_random_dir(d)
        for x in range(10):
            make_random_file(d1)
        t1 = exe_wrapper.GitWrapper(d1).init(add_all=True).commit()
        self.assertEqual(d1.lower(), t1.full_path)
        t2 = exe_wrapper.GitWrapper(d2).clone(d1)
        self.assertEqual(os.path.join(d2, os.path.basename(d1)).lower(), t2.full_path)
        t3 = exe_wrapper.GitWrapper("").clone(t2.full_path, target_directory=d3)
        self.assertEqual(d3.lower(), t3.full_path)
        t4 = exe_wrapper.GitWrapper(d).clone(t3.full_path)
        l1 = os.listdir(t1.full_path)
        l2 = os.listdir(t2.full_path)
        l3 = os.listdir(t3.full_path)
        for x in l1:
            self.assertTrue(x in l2)
            self.assertTrue(x in l3)
            if x == ".git":
                continue
            f1 = os.path.join(t1.full_path, x)
            f2 = os.path.join(t2.full_path, x)
            f3 = os.path.join(t3.full_path, x)
            self.assertTrue(file_hash(f1) == file_hash(f2) == file_hash(f3))


def remove(d):
    shutil.rmtree(d, onerror=shutil_rmtree.onerror)

if __name__ == '__main__':
    unittest.main()

