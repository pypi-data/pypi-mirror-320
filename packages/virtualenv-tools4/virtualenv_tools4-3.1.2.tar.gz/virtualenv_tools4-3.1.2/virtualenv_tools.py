#!/usr/bin/env python
"""
    move-virtualenv
    ~~~~~~~~~~~~~~~

    A helper script that moves virtualenvs to a new location.

    It only supports POSIX based virtualenvs and at the moment.

    :copyright: (c) 2012 by Fireteam Ltd.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import annotations

import argparse
import marshal
import os.path
import re
import shlex
import shutil
import sys
from types import CodeType
from typing import NamedTuple
from typing import Sequence


ACTIVATION_SCRIPTS = [
    'activate',
    'activate.csh',
    'activate.fish',
    'activate.xsh',
]
_pybin_match = re.compile(r'^python\d+\.\d+$')
_pypy_match = re.compile(r'^pypy\d+.\d+$')
_activation_path_re = re.compile(
    r'^(?:set -gx |setenv |)VIRTUAL_ENV[ =][\'"]?(.*?)[\'"]?\s*$',
)
VERBOSE = False
# magic length
# + 4 byte timestamp
# + 4 byte "size" hint was added to pyc files
# PEP 552 (implemented in python 3.7) extends this by another word
MAGIC_LENGTH = 4 + 4 + 4 + 4


def debug(msg: str) -> None:
    if VERBOSE:
        print(msg)


def update_activation_script(script_filename: str, new_path: str) -> None:
    """Updates the paths for the activate shell scripts."""
    with open(script_filename) as f:
        lines = list(f)

    def _handle_sub(match: re.Match[str]) -> str:
        text = match.group()
        start, end = match.span()
        g_start, g_end = match.span(1)
        return text[:(g_start - start)] + new_path + text[(g_end - end):]

    changed = False
    for idx, line in enumerate(lines):
        new_line = _activation_path_re.sub(_handle_sub, line)
        if line != new_line:
            lines[idx] = new_line
            changed = True

    if changed:
        debug('A %s' % script_filename)
        with open(script_filename, 'w') as f:
            f.writelines(lines)


def path_is_within(path: bytes, within: bytes) -> bool:
    relpath = os.path.relpath(path, within)
    return not relpath.startswith(b'.')


def update_script(
        script_filename: str,
        old_path_s: str,
        new_path_s: str,
) -> None:
    """Updates shebang lines for actual scripts."""
    filesystem_encoding = sys.getfilesystemencoding()
    old_path = old_path_s.encode(filesystem_encoding)
    new_path = new_path_s.encode(filesystem_encoding)

    with open(script_filename, 'rb') as f:
        if f.read(2) != b'#!':
            return
        f.seek(0)
        lines = list(f)

    # is this a python script being run under a bourne exec call
    if (
            len(lines) >= 2 and
            lines[0] == b'#!/bin/sh\n' and
            lines[1].startswith(b"'''exec' ")
    ):
        args = lines[1].strip().split()

        if path_is_within(args[1], old_path):
            new_bin = os.path.join(
                new_path,
                os.path.relpath(args[1], old_path)
            )
        else:
            return

        args[1] = new_bin
        lines[1] = b' '.join(args) + b'\n'
    else:
        args = lines[0][2:].strip().split()

        if not args:
            return

        if path_is_within(args[0], old_path):
            new_bin = os.path.join(
                new_path,
                os.path.relpath(args[0], old_path)
            )
        else:
            return

        args[0] = new_bin
        lines[0] = b'#!' + b' '.join(args) + b'\n'

    debug('S %s' % script_filename)
    with open(script_filename, 'wb') as f:
        f.writelines(lines)


def update_scripts(
        bin_dir: str,
        orig_path: str,
        new_path: str,
        activation: bool = False,
) -> None:
    """Updates all scripts in the bin folder."""
    for fname in os.listdir(bin_dir):
        path = os.path.join(bin_dir, fname)
        if fname in ACTIVATION_SCRIPTS and activation:
            update_activation_script(path, new_path)
        elif os.path.isfile(path):
            update_script(path, orig_path, new_path)


def update_pyc(filename: str, new_path: str) -> None:
    """Updates the filenames stored in pyc files."""
    with open(filename, 'rb') as rf:
        magic = rf.read(MAGIC_LENGTH)
        try:
            code = marshal.load(rf)
        except Exception:
            print('Error in %s' % filename)
            raise

    def _process(code: CodeType) -> CodeType:
        consts = []
        for const in code.co_consts:
            if type(const) is CodeType:
                const = _process(const)
            consts.append(const)
        if new_path != code.co_filename or consts != list(code.co_consts):
            code = code.replace(co_filename=new_path, co_consts=tuple(consts))
        return code

    new_code = _process(code)

    if new_code is not code:
        debug('B %s' % filename)
        with open(filename, 'wb') as wf:
            wf.write(magic)
            marshal.dump(new_code, wf)


def update_pycs(lib_dir: str, new_path: str) -> None:
    """Walks over all pyc files and updates their paths."""
    def get_new_path(filename: str) -> str:
        filename = os.path.normpath(filename)
        return os.path.join(new_path, filename[len(lib_dir) + 1:])

    for dirname, dirnames, filenames in os.walk(lib_dir):
        for filename in filenames:
            if (
                    filename.endswith(('.pyc', '.pyo')) and
                    # python 2, virtualenv 20.x symlinks os.pyc
                    not os.path.islink(os.path.join(dirname, filename))
            ):
                filename = os.path.join(dirname, filename)
                local_path = get_new_path(filename)
                update_pyc(filename, local_path)


def _update_pth_file(pth_filename: str, orig_path: str) -> None:
    with open(pth_filename) as f:
        lines = f.readlines()
    changed = False
    for i, line in enumerate(lines):
        val = line.strip()
        if val.startswith('import ') or not os.path.isabs(val):
            continue
        changed = True
        relto_original = os.path.relpath(val, orig_path)
        # If we are moving a pypy venv the site-packages directory
        # is in a different location than if we are moving a cpython venv
        relto_pth = os.path.join(
            '../../..',   # venv/lib/pythonX.X/site-packages
            relto_original
        )
        lines[i] = f'{relto_pth}\n'
    if changed:
        with open(pth_filename, 'w') as f:
            f.write(''.join(lines))
        debug(f'P {pth_filename}')


def update_pth_files(site_packages: str, orig_path: str) -> None:
    """Converts /full/paths in pth files to relative relocatable paths."""
    for filename in os.listdir(site_packages):
        filename = os.path.join(site_packages, filename)
        if filename.endswith('.pth') and os.path.isfile(filename):
            _update_pth_file(filename, orig_path)


def remove_local(base: str) -> None:
    """On some systems virtualenv seems to have something like a local
    directory with symlinks.  This directory is safe to remove in modern
    versions of virtualenv.  Delete it.
    """
    local_dir = os.path.join(base, 'local')
    if os.path.exists(local_dir):  # pragma: no cover (not all systems)
        debug(f'D {local_dir}')
        shutil.rmtree(local_dir)


def update_paths(venv: Virtualenv, new_path: str) -> None:
    """Updates all paths in a virtualenv to a new one."""
    update_scripts(venv.bin_dir, venv.orig_path, new_path)
    for lib_dir in venv.lib_dirs:
        update_pycs(lib_dir, new_path)
    update_pth_files(venv.site_packages, venv.orig_path)
    remove_local(venv.path)
    update_scripts(venv.bin_dir, venv.orig_path, new_path, activation=True)


def get_orig_path(venv_path: str) -> str:
    """This helps us know whether someone has tried to relocate the
    virtualenv
    """
    activate_path = os.path.join(venv_path, 'bin/activate')

    with open(activate_path) as activate:
        venv_var_prefix = 'VIRTUAL_ENV='
        in_case_block = False
        case_path = None
        system = None

        for line in activate:
            if 'case "$(uname)" in' in line:
                in_case_block = True
            elif in_case_block and ';;' in line:
                in_case_block = False
                if case_path:
                    return case_path
            elif in_case_block and venv_var_prefix in line:
                # Determine which OS we're on
                if not system:
                    import platform
                    system = platform.system().lower()
                if system in ['cygwin', 'msys', 'mingw']:
                    if 'CYGWIN*|MSYS*|MINGW*' in line:
                        case_path = line.split(venv_var_prefix)[1].split(')')[0].strip().strip("'\"")
                else:
                    case_path = line.split(venv_var_prefix)[1].strip().strip("'\"")
            elif line.startswith('export ') and venv_var_prefix in line:
                return line.split('=')[1].strip().strip("'\"")

        if not case_path:
            raise AssertionError('Could not find VIRTUAL_ENV= in activation script: %s' % activate_path)
        return case_path

class NotAVirtualenvError(ValueError):
    def __str__(self) -> str:
        return '{} is not a virtualenv: not a {}: {}'.format(*self.args)


class Virtualenv(NamedTuple):
    path: str
    bin_dir: str
    lib_dirs: list[str]
    site_packages: str
    orig_path: str


def _get_original_state(path: str) -> Virtualenv:
    is_pypy = os.path.isfile(os.path.join(path, 'bin', 'pypy'))
    bin_dir = os.path.join(path, 'bin')
    base_lib_dir = os.path.join(path, 'lib')
    activate_file = os.path.join(bin_dir, 'activate')

    for dir_path in (bin_dir, base_lib_dir):
        if not os.path.isdir(dir_path):
            raise NotAVirtualenvError(path, 'directory', dir_path)
    if not os.path.isfile(activate_file):
        raise NotAVirtualenvError(path, 'file', activate_file)

    matcher = _pypy_match if is_pypy else _pybin_match
    lib_dirs = [
        os.path.join(base_lib_dir, potential_lib_dir)
        for potential_lib_dir in os.listdir(base_lib_dir)
        if matcher.match(potential_lib_dir)
    ]
    if len(lib_dirs) != 1:
        raise NotAVirtualenvError(
            path,
            'directory',
            os.path.join(base_lib_dir, 'pypy#.#)' if is_pypy else 'python#.#'),
        )
    lib_dir, = lib_dirs

    site_packages = os.path.join(lib_dir, 'site-packages')
    if not os.path.isdir(site_packages):
        raise NotAVirtualenvError(path, 'directory', site_packages)

    return Virtualenv(
        path=path,
        bin_dir=bin_dir,
        lib_dirs=[lib_dir],
        site_packages=site_packages,
        orig_path=get_orig_path(path),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--update-path',
        required=True,
        help=(
            'Update the path for all required executables and helper files '
            'that are supported to the new python prefix.  You can also set '
            'this to "auto" for autodetection.'
        ),
    )
    parser.add_argument(
        '--verbose', action='store_true', help='show a listing of changes',
    )
    parser.add_argument('path', default='.', nargs='?')
    args = parser.parse_args(argv)

    global VERBOSE
    VERBOSE = args.verbose

    if args.update_path == 'auto':
        update_path = os.path.abspath(args.path)
    else:
        update_path = args.update_path

    if not os.path.isabs(update_path):
        print(f'--update-path must be absolute: {update_path}')
        return 1

    try:
        venv = _get_original_state(path=args.path)
    except NotAVirtualenvError as e:
        print(e)
        return 1

    if venv.orig_path == update_path:
        print(f'Already up-to-date: {venv.path} ({update_path})')
        return 0

    update_paths(venv, update_path)
    print(f'Updated: {venv.path} ({venv.orig_path} -> {update_path})')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
