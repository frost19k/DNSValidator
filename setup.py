#!/usr/bin/env python3

import sys
from pkg_resources import parse_version
from setuptools import setup, __version__

if parse_version(__version__) < parse_version('62.6'):
    print('Your setuptools version is incompatible with this package. Upgrade setuptools to continue the installation.')
    sys.exit(1)

if __name__ == '__main__':
    setup()
