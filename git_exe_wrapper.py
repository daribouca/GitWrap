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
import custom_path
import shutil_rmtree
import git_exceptions
import shlex
import os
import shutil
import logging
import re

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
        self.git_exe = None
        if path_to_git_exe is not None:
            self.try_git_in(path_to_git_exe)
        else:
            for x in standard_git_locations:
                self.try_git_in(x)
        if self.git_exe is None:
            raise git_exceptions.CannotFindGitExecutable()

    def try_git_in(self, path):
        try:
            subprocess.Popen(path)
            self.git_exe = x
        except FileNotFoundError:
            pass

##class GitWrapper():
##
##    git_exe = Path("git-portable/bin/git.exe")
##
##    def __init__(self, local_repo, timeout=15, git_exe=None, must_be_empty=False):
##        if git_exe is not None:
##            self.git_exe = Path(git_exe)
##        if not self.git_exe.exists:
##            raise git_exceptions.CannotFindGitExecutable("could not find Git exe in path: {}".format(self.git_exe))
##        self._local = Path(local_repo)
##        if must_be_empty and not self._local.isempty:
##            raise git_exceptions.GitWrapperException("local repo is not empty: {}".format(self._local))
##        self._wkdir = Path(self._local)
##        self._cmd = None
##        self._timeout = 15
##        self._out = "INIT NEW REPO: {}\n".format(local_repo)
##        self._last_outs = None
##        self._last_errs = None
##        self._return_code = None
##        self._running = False
##        self._ran = False
##        self._is_init = self._local.isarepo
##        self._nothing_to_commit = False
##        self._local_already_exists_and_is_not_empty = False
##
##    def _set_wkdir(self, wkdir):
##        wkdir = Path(wkdir)
##        if not wkdir.exists:
##            raise git_exceptions.GitWrapperException("Local working dir does not exist: {}".format(wkdir.full_path))
##        self._wkdir = wkdir
##        return self
##
##    def set_timeout(self, timeout):
##        if not isinstance(timeout, int) or 1 > timeout or timeout > 120:
##            raise git_exceptions.GitWrapperException("Invalid timeout: {}".format(timeout))
##        self._timeout = timeout
##        return self
##
##    def _set_cmd(self, cmd):
##        if not isinstance(cmd, list):
##            raise git_exceptions.GitWrapperException("CMD must be a LIST of STR: {}".format(cmd))
##        for x in cmd:
##            if not isinstance(x, str):
##                raise git_exceptions.GitWrapperException("CMD must be a LIST of STR: {}\n{} is not a string".format(cmd, x))
##        self._cmd = [x for x in cmd if x != ""]
##        self._cmd.insert(0, self.git_exe.full_path)
##        return self
##
##    def _run(self):
##        if not self._wkdir.exists:
##            raise git_exceptions.GitWrapperException("RUN: WKDIR does not exist: {}".format(self._wkdir.nice_full_path))
##        self._running = True
##        self._out += "WKDIR: {}\n".format(self._wkdir.nice_full_path)
##        self._out += "RUNNING: {}\n".format(self._cmd)
##        proc = Popen(args=self._cmd, cwd=self._wkdir.full_path, stdin=PIPE, stderr=PIPE, stdout=PIPE, shell=True, universal_newlines=True, start_new_session=True)
##        try:
##            outs, errs = proc.communicate(timeout=self._timeout)
##            if outs:
##                self._out += outs
##                self._last_outs = outs
##            else: self._last_outs = None
##            if errs:
##                self._out += errs
##                self._last_errs = errs
##            else: self._last_errs = None
##        except TimeoutExpired:
##            proc.kill()
##            outs, errs = proc.communicate(timeout=self._timeout)
##            if outs:
##                self._out += outs
##                self._last_outs = outs
##            else: self._last_outs = None
##            if errs:
##                self._errs += errs
##                self._last_errs = errs
##            else: self._last_errs = None
##        self._running = False
##        self._ran = True
##        self._return_code = proc.returncode
##        self._out += "=======================================\n"
##        if self._return_code != 0:
##            self._parse_output()
##            raise git_exceptions.GitWrapperException("RUN: error not handled:\n\nCMD:{}\nWKDIR:{}\nLAST OUT:{}\nLAST ERR:{}\n\nReturn code: {}".format(self._cmd, self._wkdir, self._last_outs, self._last_errs, self._return_code))
##        self._parse_output()
##        return self
##
##    def _parse_output(self):
##        if self._last_outs is not None:
##            s_out = self._last_outs.split("\n")
##            for s in [
##                'nothing added to commit but untracked files present (use "git add" to track)',
##                'nothing to commit (create/copy files and use "git add" to track)',
##                'nothing to commit, working directory clean'
##            ]:
##                if s in s_out:
##                    self._nothing_to_commit = True
##        if self._last_errs is not None:
##            if "fatal: destination path '{}' already exists and is not an empty directory.".format(self._local.basename) in self._last_errs.split("\n"):
##                self._local_already_exists_and_is_not_empty = True
##                raise git_exceptions.GitRepositoryAlreadyExistsAndIsNotEmpty(self._local.nice_full_path)
##
##    @property
##    def out(self):
##        return self._out
##
##    def clear_history(self):
##        self._out = ""
##
##    @property
##    def return_code(self):
##        return self._return_code
##
##    @property
##    def full_path(self):
##        return self._local.nice_full_path
##
##    def init(self, bare=False, add_all=False):
##        wkdir = Path(self._local.dirname)
##        repo = Path(self._local.basename)
##        if self._local.exists:
##            if self._local.isafile:
##                raise git_exceptions.GitWrapperException("INIT: local repository is a file: {}".format(repo))
##        cmd = [
##            "init",
##            "--bare" if bare else "",
##            shlex.quote(repo.basename)
##        ]
##        self._set_wkdir(wkdir)._set_cmd(cmd)._run()._set_wkdir(self._local)
##        if add_all:
##            self._set_cmd(["add","."])._run()
##        return self
##
##    def status(self):
##        self._set_cmd(["status"])._run()
##        return self
##
##    def __str__(self):
##        return self._out
##
##    def add(self, files=".",):
##        if isinstance(files, str):
##            files=[shlex.quote(files)]
##        elif isinstance(files, list):
##            files = [shlex.quote(f) for f in files]
##        else:
##            raise git_exceptions.GitWrapperException("ADD: files can only be STR or LIST\nReceived {} ({})".format(files, type(files)))
##        self._nothing_to_commit = False
##        cmd = [
##            "add"
##        ]
##        for f in files:
##            cmd.append(f)
##        try:
##            self._set_cmd(cmd)._run()
##        except git_exceptions.GitWrapperException:
##            if self._nothing_to_commit:
##                pass
##            else:
##                raise
##        return self
##
##    def commit(self, files="-a", msg="auto-commit", amend=False, dry_run=False):
##        if isinstance(files, str):
##            files=[shlex.quote(files)]
##        elif isinstance(files, list):
##            files = [shlex.quote(f) for f in files]
##        else:
##            raise git_exceptions.GitWrapperException("COMMIT: files can only be STR or LIST\nReceived {} ({})".format(files, type(files)))
##        self._nothing_to_commit = False
##        cmd = [
##            "commit",
##            "--amend" if amend else "",
##            "--dry-run" if dry_run else "",
##            "-m {}".format(shlex.quote(msg))
##        ]
##        for f in files:
##            cmd.append(f)
##        try:
##            self._set_wkdir(self._local)._set_cmd(cmd)._run()
##        except git_exceptions.GitWrapperException:
##            if self._nothing_to_commit:
##                pass
##            else:
##                raise
##        return self
##
##    def push(self, remote_name="origin", branch="master", with_tags=True, force=False, dry_run=False, prune=False, mirror=False):
##        if not self._local.exists:
##            raise git_exceptions.GitWrapperException("PUSH: local repo does not exist yet: {}".format(self._local.full_path))
##        remote_name = shlex.quote(remote_name) if remote_name else ""
##        branch = shlex.quote(branch) if branch else ""
##        cmd = [
##            "push",
##            remote_name,
##            branch,
##            "--tags" if with_tags else "",
##            "--force" if force else "",
##            "--prune" if prune else "",
##            "-n" if dry_run else "",
##            "--mirror" if mirror else "",
##        ]
##        self._set_wkdir(self._local)._set_cmd(cmd)._run()
##        return self
##
##    def pull(self, remote_name="origin", branch="master", update_submodules=False, no_commit=False,
##            no_fast_forward=False, only_fast_forward=False, rebase=False):
##        if not self._local.exists:
##            raise git_exceptions.GitWrapperException("PULL: local repo does not exist yet: {}".format(self._local.full_path))
##        remote_name, branch = shlex.quote(remote_name), shlex.quote(branch)
##        cmd = [
##            "pull",
##            "--recurse-submodules" if update_submodules else "",
##            "--no-commit" if no_commit else "",
##            "--no-ff" if no_fast_forward else "",
##            "--ff-only" if only_fast_forward else "",
##            "--rebase" if rebase else "",
##            remote_name,
##            branch
##        ]
##        self._set_wkdir(self._local)._set_cmd(cmd)._run()
##        return self
##
##    def clone(self, remote_address, target_directory=None, bare=False, recursive=True,
##                branch=None, no_checkout=False, add_as_origin=False):
##        if target_directory is not None:
##            target_directory = Path(target_directory)
##            self._set_wkdir(target_directory.dirname)
##        cmd = [
##            "clone",
##            "--bare" if bare else "",
##            "--recursive" if recursive else "",
##            "--branch {}".format(shlex.quote(branch)) if branch is not None else "",
##            "--no-checkout" if no_checkout else "",
##            remote_address,
####            shlex.quote(Path(remote_address).nice_full_path),
##            shlex.quote(Path(target_directory).basename) if target_directory is not None else ""
##        ]
##        if target_directory is None:
##            self._local = Path(os.path.join(self._wkdir.full_path, Path(remote_address).basename))
##        else:
##            self._local = Path(target_directory)
##        self._set_cmd(cmd)._run()
##        if add_as_origin:
##            self._set_cmd([
##                "remote",
##                'add',
##                'origin',
##                remote_address
##            ])._run()
##        return self

if __name__ == "__main__":
    git_executable()
    print(git_exe)

