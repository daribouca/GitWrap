#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
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

class Path():
    def __init__(self, p):
        if isinstance(p, Path):
            self.p = p.p
        elif isinstance(p, str):
            self.p = p
        else:
            raise Exception("Path only accepts String or other Path as input")
    @property
    def nice_path(self):
        return os.path.normcase(os.path.normpath(self.p))
    @property
    def nice_full_path(self):
        return os.path.normcase(os.path.normpath(self.abs))
    @property
    def full_path(self):
        return self.abs
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
        return self.type == "dir"
    @property
    def isempty(self):
        if self.isafile:
            if os.stat(self.full_path).st_size == 0:
                return True
        elif not os.listdir(self.full_path):
            return True
        return False
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
    def __repr__(self):
        return self.__str__()
    def remove(self):
        if self.isafile:
            os.remove(self.full_path)
        elif self.isadir:
            shutil.rmtree(self.full_path, onerror=shutil_rmtree.onerror)
