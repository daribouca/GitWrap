#-------------------------------------------------------------------------------
# Name:        exe_wrapper
# Purpose:     wraps around system-agnostic git executable
#
# Author:      bob
#
# Created:     28/10/2013
# Copyright:   (c) bob 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import subprocess
import shlex
import os
import shutil
import logging
import re

import GitWrap.custom_path
import GitWrap.shutil_rmtree
import GitWrap.git_exceptions

"""
VALID REPOS URLs:


    ssh://[user@]host.xz[:port]/path/to/repo.git/

    git://host.xz[:port]/path/to/repo.git/

    http[s]://host.xz[:port]/path/to/repo.git/

    ftp[s]://host.xz[:port]/path/to/repo.git/

    rsync://host.xz/path/to/repo.git/

An alternative scp-like syntax may also be used with the ssh protocol:

    [user@]host.xz:path/to/repo.git/

The ssh and git protocols additionally support ~username expansion:

    ssh://[user@]host.xz[:port]/~[user]/path/to/repo.git/

    git://host.xz[:port]/~[user]/path/to/repo.git/

    [user@]host.xz:/~[user]/path/to/repo.git/

For local repositories, also supported by git natively, the following syntaxes may be used:

    /path/to/repo.git/

    file:///path/to/repo.git/

"""

class GitExeWrapper():

    standard_git_locations = ["git",os.path.abspath("git-portable/bin/git.exe")]

    def __init__(self, path_to_git_exe=None):
        self.look_for_git_in(path_to_git_exe)

    def look_for_git_in(self, path=None):
        self.git_exe = None
        if path is not None:
            self.try_git_in(path)
        else:
            for x in GitExeWrapper.standard_git_locations:
                self.try_git_in(x)
        if self.git_exe is None:
            raise GitWrap.git_exceptions.CannotFindGitExecutable()

    def try_git_in(self, path):
        try:
            subprocess.Popen(path)
            self.git_exe = GitWrap.custom_path.File(path)
        except FileNotFoundError:
            pass

    @property
    def version(self):
        """returns Git exe version string"""
        pass


if __name__ == "__main__":
    g = GitExeWrapper()
    print(g.git_exe)

