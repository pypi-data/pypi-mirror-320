[![Build Status](https://github.com/HLFH/virtualenv-tools/actions/workflows/main.yml/badge.svg?query=branch%3Amain)](https://github.com/HLFH/virtualenv-tools/actions/workflows/main.yml)
[![Coverage Status](https://img.shields.io/coveralls/HLFH/virtualenv-tools.svg?branch=master)](https://coveralls.io/r/HLFH/virtualenv-tools)
[![PyPI version](https://badge.fury.io/py/virtualenv-tools3.svg)](https://pypi.python.org/pypi/virtualenv-tools4)

virtualenv-tools4
--------

virtualenv-tools4 is a fork of [virtualenv-tools3](https://github.com/Yelp/virtualenv-tools) (now
unmaintained) which adds support for Python 3.12, among other things. Full patch details are below.

## virtualenv-tool4 patch

* Add Python 3.12 & 3.13 support.

##  virtualenv-tool3 (yelp) patches

### yelp4

* Add python3 support
* Drop python2.6 support
* 100% test coverage
* Removes `$VENV/local` instead of fixing up symlinks
* Removed `--reinitialize`, instead run `virtualenv $VENV -p $PYTHON`
* Rewrite .pth files to relative paths


### yelp3

* default output much more concise, added a --verbose option
* improved fault tolerance, in the case of:
    * corrupt pyc files
    * broken symlinks
    * unexpected directories
* no-changes-needed is a success case (idempotency exits 0)


### yelp1

* --update now works more generally and reliably (e.g. virtualenv --python=python2.7)


## How-to

This repository contains scripts for
deployment of Python code.  We're using them in combination with
salt to build code on one server on a self contained virtualenv
and then move that over to the destination servers to run.

### Why not virtualenv --relocatable?

For starters: because it does not work.  relocatable is very
limited in what it does and it works at runtime instead of
making the whole thing actually move to the new location.  We
ran into a ton of issues with it and it is currently in the
process of being phased out.

### Why would I want to use it?

The main reason you want to use this is for build caching.  You
have one folder where one virtualenv exists, you install the
latest version of your codebase and all extensions in there, then
you can make the virtualenv relocate to a target location, put it
into a tarball, distribute it to all servers and done!

### Example flow:

First time: create the build cache

```
$ mkdir /tmp/build-cache
$ virtualenv --distribute /tmp/build-cache
```

Now every time you build:

```
$ . /tmp/build-cache/bin/activate
$ pip install YourApplication
```

Build done, package up and copy to whatever location you want to have it.

Once unpacked on the target server, use the virtualenv tools to
update the paths and make the virtualenv magically work in the new
location.  For instance we deploy things to a path with the
hash of the commit in:

```
$ virtualenv-tools --update-path /srv/your-application/<hash>
```

Compile once, deploy whereever.  Virtualenvs are completely self
contained.  In order to switch the current version all you need to
do is to relink the builds.
