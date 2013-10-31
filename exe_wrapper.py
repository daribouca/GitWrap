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

git_exe = os.path.abspath("git-portable/bin/git.exe")
tests_path = os.path.join(os.curdir, "tests")
tests = {}
for x in ["repo1","repo2","wkdir1","wkdir2","wkdir3","wkdir4"]:
    tests[x] = os.path.abspath(os.path.join(tests_path, x))

class GitWrapperException(Exception):
    def __init__(self, msg):
        print(msg)

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

def exec(cmd="", wd="."):
    print("====== BEGIN GIT EXEC ======")
    wd = os.path.abspath(wd)
    cmd = shlex.split(cmd)
    print("Wkdir: {}\nCommand: {}\n".format(wd, " ".join(cmd)))
    cmd.insert(0, git_exe)
    proc = Popen(cmd, cwd=wd, stdin=PIPE, stderr=PIPE, stdout=PIPE, shell=True, universal_newlines=True, start_new_session=True)
    print("====== BEGIN GIT OUTPUT ======")
    try:
        outs, errs = proc.communicate(timeout=15)
        print(outs, errs)
    except TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate()
        print("====== PROCESS TIMED OUT ======")
        print(outs, errs)
    print("====== END OF GIT OUTPUT ======")
    print("====== END OF GIT EXEC ======")
    return (outs, errs, proc.returncode)

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

    init_test_repo = os.path.join(tests_path, "test_init")
    init(init_test_repo)
##    shutil.rmtree(init_test_repo, onerror=onerror)


if __name__ == '__main__':
    main()
