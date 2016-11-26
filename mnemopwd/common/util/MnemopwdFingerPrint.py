#!/usr/bin/env python3
# coding: utf-8

# Copyright (c) 2016, Thierry Lemeunier <thierry at lemeunier dot net>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


from os import path
from pathlib import Path
import hashlib

here = path.abspath(path.dirname(__file__))


class MnemopwdFingerPrint:
    """Mechanism to control code has not been modified"""

    path_list = ['serverctl.py', 'clientctl.py', '__init__.py', 'common',
                 'pyelliptic', 'client', 'server']
    module_list = []

    def create_module_list(self, prefix=None):
        """Create a sorted module list"""
        self.module_list = []
        self._create_module_list(self.path_list, prefix)
        self.module_list.sort()

    def _create_module_list(self, plist, prefix):
        """Get module names from the path list given"""
        for pa in plist:
            # Add prefix if exists
            if prefix is not None:
                pa = path.join(prefix, pa)
            ap = Path(pa)
            # Browse or add
            if ap.is_dir() and ap.name != '__pycache__':
                for child in ap.iterdir():
                    if child.is_dir() and child.name != '__pycache__':
                        self._create_module_list([str(child)], prefix)
                    elif child.suffix == '.py':
                        self.module_list.append(str(child))
            elif ap.exists():
                self.module_list.append(pa)

    def compute_fingerprint(self):
        """Compute fingerprint"""
        h = hashlib.sha256()
        for name in self.module_list:
            with open(name, mode='rb') as hfile:
                source = hfile.read()  # Get the source code
            h.update(source)  # Feed hash engine with each source string
        return h.hexdigest()  # Get hash in hexadecimal format

    def control_fingerprint(self, prefix):
        """Control the fingerprint"""
        self.module_list = []
        self.create_module_list(prefix=prefix)
        the_fingerprint = self.compute_fingerprint()
        try:
            with open(path.join(here, "fingerprint"), 'rb') as hfile:
                fingerprint_from_file = (hfile.read()).decode()
                if fingerprint_from_file != the_fingerprint:
                    print("it seems source code has been modified, so server can not be launched")
                    exit(1)
        except FileNotFoundError:
            print("source code has been modified, so server can not be launched")
            exit(1)

if __name__ == "__main__":
    # Control the execution path
    if not Path("serverctl.py").exists():
        print("This script must be launched from mnemopwd directory")
        exit(1)
    # Delete fingerprint file
    p = Path(path.join(here, "fingerprint"))
    if p.exists():
        p.unlink()
    # Compute fingerprint
    mnemofg = MnemopwdFingerPrint()
    mnemofg.create_module_list()
    fingerprint = mnemofg.compute_fingerprint()
    # Save fingerprint
    with open(path.join(here, "fingerprint"), 'wb') as file:
        file.write(fingerprint.encode())
