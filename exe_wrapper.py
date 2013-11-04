#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      owner
#
# Created:     28/10/2013
# Copyright:   (c) owner 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

from subprocess import Popen, PIPE, TimeoutExpired
from path import Path
from git_exceptions import GitWrapperException
from shutil_rmtree import onerror
import shlex
import os
import shutil
import stat
import logging

logger = logging.getLogger()
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

git_exe = os.path.abspath("git-portable/bin/git.exe")
tests_path = os.path.join(os.curdir, "tests")
tests = {}
for x in ["repo1","repo2","wkdir1","wkdir2","wkdir3","wkdir4"]:
    tests[x] = os.path.abspath(os.path.join(tests_path, x))


##        print(msg)

class GitWrapper():

    git_exe = Path("git-portable/bin/git.exe")

    def __init__(self, local_repo, timeout=15):
        if not self.git_exe.exists:
            raise GitWrapperException("could not find Git exe: {}".format(self.git_exe))
        self._local = Path(local_repo)
        self._wkdir = Path(self._local)
        self._cmd = None
        self._timeout = 15
        self._out = "INIT: "
        self._last_outs = None
        self._last_errs = None
        self._return_code = None
        self._running = False
        self._ran = False
        self._is_init = self._local.isarepo
        self._nothing_to_commit = False

    def _set_wkdir(self, wkdir):
        wkdir = Path(wkdir)
        if not wkdir.exists:
            raise GitWrapperException("Local working dir does not exist: {}".format(wkdir.full_path))
        self._wkdir = wkdir
        return self

    def set_timeout(self, timeout):
        self._timeout = timeout
        return self

    def _set_cmd(self, cmd):
        if not isinstance(cmd, list):
            raise GitWrapperException("CMD must be a STR: {}".format(cmd))
##        self._cmd = "{} {}".format(shlex.quote(self.git_exe.full_path), cmd)
##        self._cmd = [self.git_exe.full_path, cmd]
        self._cmd = [x for x in cmd if x != ""]
        self._cmd.insert(0, self.git_exe.full_path)
        return self

    def _run(self):
        self._running = True
        self._out += "WKDIR: {}\n".format(self._wkdir.nice_full_path)
##        self._out += "RUNNING: {}\n".format(" ".join([x for x in self._cmd[1:]]))
        self._out += "RUNNING: {}\n".format(self._cmd)
        proc = Popen(args=self._cmd, cwd=self._wkdir.full_path, stdin=PIPE, stderr=PIPE, stdout=PIPE, shell=True, universal_newlines=True, start_new_session=True)
        try:
            outs, errs = proc.communicate(timeout=self._timeout)
            if outs:
                self._out += outs
                self._last_outs = outs
            else: self._last_outs = None
            if errs:
                self._errs += errs
                self._last_errs = errs
            else: self._last_errs = None
        except TimeoutExpired:
            proc.kill()
            outs, errs = proc.communicate(timeout=self._timeout)
            if outs:
                self._out += outs
                self._last_outs = outs
            else: self._last_outs = None
            if errs:
                self._errs += errs
                self._last_errs = errs
            else: self._last_errs = None
        self._running = False
        self._ran = True
        self._return_code = proc.returncode
        self._out += "=======================================\n"
        if self._return_code != 0:
            self._parse_output()
            raise GitWrapperException("RUN: error not handled:\n\n{}\n\nReturn code: {}".format(self._out, self._return_code))
        self._parse_output()
        return self

    def _parse_output(self):
        if 'nothing to commit (create/copy files and use "git add" to track)' in self._last_outs.split("\n"):
            self._nothing_to_commit = True

    @property
    def out(self):
        return self._out

    def clear_history(self):
        self._out = ""

    @property
    def return_code(self):
        return self._return_code

    def init(self, bare=False):
        cmd = ["init"]
        wkdir = Path(self._local.dirname)
        repo = Path(self._local.basename)
        if repo.exists:
            if repo.isafile:
                raise GitWrapperException("INIT: local repository is a file: {}".format(repo))
        if bare:
##            cmd = "{} --bare".format(cmd)
            cmd.append("--bare")
##        cmd = "{} {}".format(cmd, shlex.quote(repo.basename))
        cmd.append(shlex.quote(repo.basename))
        self._set_wkdir(wkdir)._set_cmd(cmd)._run()._set_wkdir(self._local)

    def status(self):
        self._set_cmd(["status"])._run()

    def __str__(self):
        return self._out

    def commit(self, files="-a", msg="auto-commit", amend=False, dry_run=False):
        if isinstance(files, str):
            files=[shlex.quote(files)]
        elif isinstance(files, list):
            files = [shlex.quote(f) for f in files]
        else:
            raise GitWrapperException("COMMIT: files can only be STR or LIST\nReceived {} ({})".format(files, type(files)))
        self._nothing_to_commit = False
        cmd = ["commit"]
        cmd.append("--amend" if amend else "")
        cmd.append("--dry-run" if dry_run else "")
        cmd.append("-m {}".format(shlex.quote(msg)))
        cmd.append(" ".join(files))
        try:
            self._set_cmd(cmd)._run()
        except GitWrapperException:
            if self._nothing_to_commit:
                pass
            else:
                raise


def push(wkdir, remote_name="origin", branch="master"):
    if not os.path.exists(wkdir):
        raise GitWrapperException("PUSH: wkdir does not exist:\n\n\
        Wkdir: {}\n\n\
        Full path:{}".format(wkdir, os.path.abspath(wkdir)))
    remote_name = shlex.quote(remote_name)
    branch = shlex.quote(branch)
    outs, errs, return_code = exec("push {} {}".format(remote_name, branch), wd=wkdir)
    if return_code != 0:
        raise GitWrapperException("PUSH: unhandled error:\n{}".format(errs))

def pull(wkdir, remote_name="origin", branch="master"):
    if not os.path.exists(wkdir):
        raise GitWrapperException("PULL: wkdir does not exist:\n\n\
        Wkdir: {}\n\n\
        Full path:{}".format(wkdir, os.path.abspath(wkdir)))
    remote_name = shlex.quote(remote_name)
    branch = shlex.quote(branch)
    outs, errs, return_code = exec("pull {} {}".format(remote_name, branch), wd=wkdir)
    if return_code != 0:
        raise GitWrapperException("PULL: unhandled error:\n{}".format(errs))

def clone(remote_address, wkdir, branch="master"):
    if os.path.exists(wkdir) and os.listdir(wkdir):
        raise GitWrapperException("CLONE: wkdir exists and is not empty:\n\n\
        Wkdir: {}\n\n\
        Full path: {}".format(os.path.basename(wkdir), wkdir))
    wkdir = os.path.abspath(wkdir)
    remote_address = shlex.quote(remote_address)
    wkdir = shlex.quote(wkdir)
    branch = shlex.quote(branch)
    outs, errs, return_code = exec("clone {} {} -b {}".format(remote_address, wkdir, branch))
    if return_code != 0:
        raise GitWrapperException("CLONE: unhandled error:\n{}".format(errs))




def main():
    t = GitWrapper("test init")
    t.init()
##    print(t)
    t.status()
##    print(t)
    t.commit(msg="caribou meuh tchoutchou")
##    p = t._out.split("\n")
##    for x in p:
##        print(x)
    print(t._last_errs)
##    print(t)
##    t.commit(files="file1")
##    print(t)
##    t.commit(files=["files 1","file 2"])
##    print(t)
####    t.commit(files=None) # MUST RAISE EXCEPTION
    t = GitWrapper("test init 2")


if __name__ == '__main__':
    main()
