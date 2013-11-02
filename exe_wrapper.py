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

class GitWrapperException(Exception):
    def __init__(self, msg):
        logging.error("GitWrapperException: {}".format(msg))
##        print(msg)

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
        self._has_pending_changes = False

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
            raise GitWrapperException("RUN: error not handled:\n\n{}\n\nReturn code: {}".format(self._out, self._return_code))
        self._parse_output()
        return self

    def _parse_output(self):
        pass

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
        cmd = ["commit"]
        if isinstance(files, str):
            files=[shlex.quote(files)]
        elif not isinstance(files, list):
            raise GitWrapperException("COMMIT: files can only be STR or LIST\nReceived {} ({})".format(files, type(files)))
        else:
            files = [shlex.quote(f) for f in files]
        cmd.append("--amend" if amend else "")
        cmd.append("--dry-run" if dry_run else "")
        cmd.append("-m {}".format(shlex.quote(msg)))
        cmd.append(" ".join(files))
        try:
            self._set_cmd(cmd)._run()
        except GitWrapperException:
            if 'nothing to commit (create/copy files and use "git add" to track)' in self._out.split("\n"):
                self._has_pending_changes = False
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

def onerror(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    if not os.access(path, os.W_OK):
        # Is the error an access error ?
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise


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
