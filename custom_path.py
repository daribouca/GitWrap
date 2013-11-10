#-------------------------------------------------------------------------------
# Name:        custom_path
# Purpose:     defines versatile File, Repo and Folder objects
#
# Author:      owner
#
# Created:     04/11/2013
# Copyright:   (c) owner 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import os
import shutil
import shutil_rmtree
import weakref

d_sizes = ["","KB","MB","GB"]

class Path():
    _PathPool = weakref.WeakValueDictionary()
    def __new__(cls, p):
        if isinstance(p, Path):
            obj = Path._PathPool.get(p.p, None)
        elif isinstance(p, str):
            obj = Path._PathPool.get(p, None)
        else:
            raise Exception("Path only accepts String or other Path as input")
        if not obj:
            obj = object.__new__(cls)
            Path._PathPool[p] = obj
            obj.p = p
        obj.full_path = obj.abs
##        obj.__str__ = obj.nice_full_path
        obj.__repr__ = obj.__str__
        return obj

    def __str__(self):
        return  self.nice_full_path

    @property
    def nice_path(self):
        return os.path.normcase(os.path.normpath(self.p))

    @property
    def nice_full_path(self):
        return os.path.normcase(os.path.normpath(self.abs))

##    @property
##    def full_path(self):
##        return self.abs



    @property
    def abs(self):
        return os.path.abspath(self.p)

    @property
    def basename(self):
        return os.path.basename(self.p)

    @property
    def isafile(self):
        return self.type == "file"

    @property
    def isadir(self):
        return self.type == "dir" or self.type == "repo"

    @property
    def type(self):
        if os.path.isdir(self.p):
            if os.path.exists(os.path.join(self.full_path, ".git")):
                return "repo"
            return "dir"
        elif os.path.isfile(self.p):
            return "file"
        else:
            return "other"

    @property
    def dirname(self):
        return os.path.dirname(self.abs)

    @property
    def exists(self):
        return os.path.exists(self.p)

    @property
    def isarepo(self):
        return self.type == "repo"

    def __str__(self):
        return self.nice_full_path

class File(Path):
    def __new__(cls, p):
        p = super().__new__(cls, p)
        if p.exists and not p.isafile:
            raise Exception("not a File: {}".format(p.full_path))
        return p
##    def __init__(self, p):
##        super().__init__(p)
##        if not self.isafile:
##            raise Exception("not a File: {}".format(p))
##        self._stat = os.stat(self.full_path)

    @property
    def size(self):
        return os.path.getsize(self.full_path)

    @property
    def nice_size(self):
        s = self.size
        u = 0
        while s > 1024:
            u += 1
            s /= 1024
        return "{:.2f}{}".format(s, d_sizes[u])

    def remove(self):
        os.remove(self.full_path)

    @property
    def isempty(self):
        if os.stat(self.full_path).st_size == 0:
            return True
        return False

class Folder(Path):
    def __new__(cls, p):
        p = super().__new__(cls, p)
        if p.exists and not p.isadir:
            raise Exception("not a Folder: {}".format(p.full_path))
        return p

    @property
    def size(self):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(self.full_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size

    @property
    def nice_size(self):
        s = self.size
        u = 0
        while s > 1024:
            u += 1
            s /= 1024
        return "{:.2f}{}".format(s, d_sizes[u])

    def remove(self):
        shutil.rmtree(self.full_path, onerror=shutil_rmtree.onerror)

    @property
    def isempty(self):
        if not os.listdir(self.full_path):
            return True
        return False

class Repo(Folder):
    def __new__(cls, p):
        p = super().__new__(cls, p)
        if p.exists and not p.isarepo:
            raise Exception("not a Repo: {}".format(p.full_path))
        return p




if __name__ == "__main__":
##    f = File("custom_path.py")
##    print(f.nice_size)
##    d = Folder("git-portable")
##    print(d.nice_size)
##    f2 = File(f)
##    print(f == f2)
##    print(f is f2)
##    print(f2.full_path)
##    print(f2)
##    print(f2.__repr__())
    r = Repo(os.getcwd())
    print(r.isempty)
