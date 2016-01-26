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

from pathlib import Path
import importlib
import inspect
import hashlib

class MnemopwdFingerPrint() :

    path_list = ['MnemopwdFingerPrint', 'serverctl', 'common', 'pyelliptic', 'server']
    module_list = []

    def create_module_list(self) :
        self._create_module_list(self.path_list)

    def _create_module_list(self, plist) :
        """Get module names from the path list given"""
        for path in plist :
            p = Path(path)
            if p.is_dir() and p.name != '__pycache__' :
                for child in p.iterdir() :
                    if child.is_dir():
                        self._create_module_list([str(child)])
                    elif child.suffix == '.py':
                        self.module_list.append(path.replace('/', '.') + '.' + child.stem)
            elif Path(path + '.py').exists() :
                self.module_list.append(path)

    def compute_fingerprint(self) :
        """Compute fingerprint"""
        h = hashlib.sha256()
        for name in self.module_list :
            module = importlib.import_module(name) # Import a module
            source = inspect.getsource(module) # Get source string of the module
            h.update(source.encode()) # Feed hash engine with each source string
        return h.hexdigest() # Get hash in hexadecimal format

    def control_fingerprint(self) :
        """Control the fingerprint"""
        self.module_list = []
        self.create_module_list()
        fingerprint = self.compute_fingerprint()
        with open("fingerprint", 'rb') as file :
            fingerprint_from_file = (file.read()).decode()
            if fingerprint_from_file != fingerprint :
                print("it seems source code has been modified, so server can not be launched")
                exit(1)

if __name__ == "__main__" :
    # Delete fingerprint file
    p = Path("fingerprint")
    if p.exists() : p.unlink()
    # Compute fingerprint
    mnemofg = MnemopwdFingerPrint()
    mnemofg.create_module_list()
    fingerprint = mnemofg.compute_fingerprint()
    # Save fingerprint
    with open("fingerprint", 'w') as file:
        file.write(fingerprint)

