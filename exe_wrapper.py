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
        print(msg)

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
        return os.path.isfile(self.full_path)
    @property
    def isadir(self):
        return os.path.isdir(self.full_path)
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
    def __str__(self):
        return self.nice_full_path
    def __repr__(self):
        return self.__str__()

class GitWrapper():

    git_exe = Path("git-portable/bin/git.exe")
    valid_commands = {
    "clone","init","checkout","push","pull"
    }

    def __init__(self, wkdir=None, cmd=None, timeout=15):
        if not self.git_exe.exists:
            raise GitWrapperException("could not find Git exe: {}".format(self.git_exe))
        self._wkdir = wkdir
        self._cmd = cmd
        self._timeout = 15
        self._outs= None
        self._errs = None
        self._return_code = None
        self._running = False
        self._ran = False

    def _set_wkdir(self, wkdir):
        wkdir = Path(wkdir)
        if not wkdir.exists:
            raise GitWrapperException("Local working dir does not exist: {}".format(wkdir.full_path))
        self._wkdir = wkdir

    def set_timeout(self, timeout):
        self._timeout = timeout

    def _set_cmd(self, cmd):
        if not isinstance(cmd, list):
            raise GitWrapperException("CMD must be a list: {}".format(cmd))
        self._cmd = cmd

    def _run(self):
        self._running = True
        proc = Popen(args=self._cmd, cwd=self._wkdir.full_path, stdin=PIPE, stderr=PIPE, stdout=PIPE, shell=True, universal_newlines=True, start_new_session=True)
        try:
            self._outs, self._errs = proc.communicate(timeout=self._timeout)
        except TimeoutExpired:
            proc.kill()
            self._outs, self._errs = proc.communicate()
        self._running = False
        self._ran = True
        self._return_code = proc.returncode

    @property
    def outs(self):
        return self._outs

    @property
    def errs(self):
        return self._errs

    @property
    def return_code(self):
        return self._return_code

    def init(self, local, bare=False):
        cmd = []
        cmd.append(self.git_exe.full_path)
        cmd.append("init")
        local = Path(local)
        if local.exists:
            if local.isafile:
                raise GitWrapperException("INIT: local is a file: {}".format(local))
            if not local.isempty:
                raise GitWrapperException("INIT: local is not empty: {}".format(local))
        if bare:
            cmd.append("--bare")
        cmd.append(local.basename)
        self._set_wkdir(local.dirname)
        self._set_cmd(cmd)
        self._run()


def init(wkdir, bare=False, add_all=False):
    if bare and add_all:
        raise GitWrapperException("INIT: can't initialize a bare repo and add files at the same time")
    if bare and os.path.exists(wkdir) and os.path.isdir(wkdir) and os.listdir(wkdir):
        raise GitWrapperException("INIT: cannot initialize non-empty bare repository: {}".format(wkdir))
    if os.path.exists(wkdir) and os.path.isfile(wkdir):
        raise GitWrapperException("INIT: file exists: {}".format(wkdir))
    s = os.path.split(os.path.abspath(wkdir))
    folder = s[0]
    repo_name = s[1]
    print(folder, repo_name)
    bare = "" if bare is False else "--bare"
    repo_name = shlex.quote(repo_name)
    exec("init {} {}".format(bare, repo_name), wd=folder)
    if add_all:
        exec("add .", wd=wkdir)

def commit(wkdir, files=None, msg="auto-commit"):
    if not os.path.exists(wkdir):
        raise GitWrapperException("COMMIT: wkdir does not exist:\n\n\
        Wkdir: {}\n\n\
        Full path:{}".format(wkdir, os.path.abspath(wkdir)))
    if files is None:
        files = "-a"
    else:
        if type(files) is list:
            files = [shlex.quote(f) for f in files]
        elif type(files) is str:
            files = shlex.quote(files)
    msg = shlex.quote(msg)
    outs, errs, return_code = exec("commit {} -m {}".format(files, msg), wd=wkdir)
    if return_code != 0:
        raise GitWrapperException("COMMIT: unhandled error:\n{}".format(errs))


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

##def exec(cmd="", wd="."):
##    print("====== BEGIN GIT EXEC ======")
##    wd = os.path.abspath(wd)
##    cmd = shlex.split(cmd)
##    print("Wkdir: {}\nCommand: {}\n".format(wd, " ".join(cmd)))
##    cmd.insert(0, git_exe)
##    proc = Popen(cmd, cwd=wd, stdin=PIPE, stderr=PIPE, stdout=PIPE, shell=True, universal_newlines=True, start_new_session=True)
##    print("====== BEGIN GIT OUTPUT ======")
##    try:
##        outs, errs = proc.communicate(timeout=15)
##        print(outs, errs)
##    except TimeoutExpired:
##        proc.kill()
##        outs, errs = proc.communicate()
##        print("====== PROCESS TIMED OUT ======")
##        print(outs, errs)
##    print("====== END OF GIT OUTPUT ======")
##    print("====== END OF GIT EXEC ======")
##    return (outs, errs, proc.returncode)

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
##    exec()
##    exec("--version")
##    exec("help merge")
##    exec("status", tests["wkdir1"])
##    exec("push", tests["wkdir1"])
##    exec("pull", tests["wkdir1"])
##    os.remove(tests["wkdir3"])

##    if os.path.exists(tests["wkdir3"]):
##        shutil.rmtree(tests["wkdir3"], onerror=onerror)
##    clone(tests["repo1"], tests["wkdir3"])
##    pull(tests["wkdir3"])
##    push(tests["wkdir3"])
##    with open(os.path.join(tests["wkdir3"], "repo1.file1.txt")) as f:
##        l = f.readlines()
##    l.append("\ntest_line_add")
##    with open(os.path.join(tests["wkdir3"], "repo1.file1.txt"), mode="w") as f:
##        f.writelines(l)
##    commit(tests["wkdir3"], "*.txt","test message")
##    exec("status",tests["wkdir3"])
##    push(tests["wkdir3"])
##    exec("update-ref HEAD \"HEAD^\"", tests["repo1"])

##    init_test_repo = os.path.join(tests_path, "test_init")
##    init(init_test_repo)
##    shutil.rmtree(init_test_repo, onerror=onerror)
##    logger.debug("test")
    t = GitWrapper()
    t.init("./test_init")
    print(t.outs)


if __name__ == '__main__':
    main()
