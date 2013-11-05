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
from custom_path import Path
from git_exceptions import GitWrapperException
from shutil_rmtree import onerror
import shlex
import os
import shutil
import stat
import logging
import re

re_valid_repo_urls = [
    re.compile(r"\Assh://(.*@)?.*\..*(:[0-9]{1,5})?(./)*\Z"),
    re.compile(r"\A(git|http(s)?|ftp(s)?)://.*\..*(:[0-9]{1,5})?(./)*\Z"),
    re.compile(r"\Arsync://.*\..*(./)*\Z"),
    re.compile(r"\A(.*@)?.*\..*(./)*\Z")
]

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

logger = logging.getLogger()
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

git_exe = os.path.abspath("git-portable/bin/git.exe")

class GitWrapper():

    git_exe = Path("git-portable/bin/git.exe")

    def __init__(self, local_repo, timeout=15, git_exe=None):
        if git_exe is not None:
            self.git_exe = Path(git_exe)
        if not self.git_exe.exists:
            raise GitWrapperException("could not find Git exe: {}".format(self.git_exe))
        self._local = Path(local_repo)
        self._wkdir = Path(self._local)
        self._cmd = None
        self._timeout = 15
        self._out = "INIT NEW REPO: {}\n".format(local_repo)
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
        if not isinstance(timeout, int) or 1 > timeout or timeout > 120:
            raise GitWrapperException("Invalid timeout: {}".format(timeout))
        self._timeout = timeout
        return self

    def _set_cmd(self, cmd):
        if not isinstance(cmd, list):
            raise GitWrapperException("CMD must be a LIST of STR: {}".format(cmd))
        for x in cmd:
            if not isinstance(x, str):
                raise GitWrapperException("CMD must be a LIST of STR: {}\n{} is not a string".format(cmd, x))
        self._cmd = [x for x in cmd if x != ""]
        self._cmd.insert(0, self.git_exe.full_path)
        return self

    def _run(self):
        self._running = True
        self._out += "WKDIR: {}\n".format(self._wkdir.nice_full_path)
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

    @property
    def full_path(self):
        return self._local.nice_full_path

    def init(self, bare=False):
        cmd = ["init"]
        wkdir = Path(self._local.dirname)
        repo = Path(self._local.basename)
        if self._local.exists:
            if self._local.isafile:
                raise GitWrapperException("INIT: local repository is a file: {}".format(repo))
        if bare:
            cmd.append("--bare")
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
        cmd = [
            "commit",
            "--amend" if amend else "",
            "--dry-run" if dry_run else "",
            "-m {}".format(shlex.quote(msg)),
            " ".join(files)
        ]
        try:
            self._set_cmd(cmd)._run()
        except GitWrapperException:
            if self._nothing_to_commit:
                pass
            else:
                raise

    def push(self, remote_name="origin", branch="master", with_tags=True, force=False, dry_run=False, prune=False, mirror=False):
        if not self._local.exists:
            raise GitWrapperException("PUSH: local repo does not exist yet: {}".format(self._local.full_path))
        remote_name, branch = shlex.quote(remote_name), shlex.quote(branch)
        cmd = [
            "push",
            "--tags" if with_tags else "",
            "--force" if force else "",
            "--prune" if prune else "",
            "-n" if dry_run else "",
            "--mirror" if mirror else "",
            remote_name,
            branch
        ]
        self._set_cmd(cmd)._run()

    def pull(self, remote_name="origin", branch="master", update_submodules=False, no_commit=False,
            no_fast_forward=False, only_fast_forward=False, rebase=False):
        if not self._local.exists:
            raise GitWrapperException("PULL: local repo does not exist yet: {}".format(self._local.full_path))
        remote_name, branch = shlex.quote(remote_name), shlex.quote(branch)
        cmd = [
            "pull",
            "--recurse-submodules" if update_submodules else "",
            "--no-commit" if no_commit else "",
            "--no-ff" if no_fast_forward else "",
            "--ff-only" if only_fast_forward else "",
            "--rebase" if rebase else "",
            remote_name,
            branch
        ]
        self._set_cmd(cmd)._run()

    def clone(self, remote_address, target_directory=None, bare=False, recursive=True,
                branch=None, no_checkout=False):
        if target_directory is not None:
            target_directory = Path(target_directory)
            self._set_wkdir(tg.dirname)
        cmd = [
            "clone", shlex.quote(remote_address),
            shlex.quote(Path(tg).basename) if target_directory is not None else "",
            "--bare" if bare else "",
            "--recursive" if recursive else "",
            "--branch {}".format(shlex.quote(branch)) if branch is not None else "",
            "--no-checkout" if no_checkout else "",
        ]
        self._set_cmd(cmd)._run()

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
    print(t)
##    print(t)
##    t.commit(files="file1")
##    print(t)
##    t.commit(files=["files 1","file 2"])
##    print(t)
####    t.commit(files=None) # MUST RAISE EXCEPTION
    t = GitWrapper("test init 2")
    print(t)


if __name__ == '__main__':
    main()
