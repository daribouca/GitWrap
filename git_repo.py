#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      owner
#
# Created:     10/11/2013
# Copyright:   (c) owner 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import git_exe_wrapper
import custom_path

class GitRepo():
    def __init__(self, repo_path, path_to_git=None):
        self.exe_wrapper = git_exe_wrapper.GitExeWrapper(path_to_git)
        self.local = custom_path.Folder(repo_path)

