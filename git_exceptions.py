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

import logging

class GitWrapperException(Exception):
    def __init__(self, msg=""):
        if msg:
            logging.error(msg)

class GitRepositoryAlreadyExistsAndIsNotEmpty(GitWrapperException):
    def __init__(self, msg=""):
        super().__init__(msg)

class CannotFindGitExecutable(GitWrapperException):
    def __init__(self, msg=""):
        super().__init__(msg)