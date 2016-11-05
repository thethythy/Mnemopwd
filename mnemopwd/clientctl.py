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


import time
from os import path

from .common.util.MnemopwdFingerPrint import MnemopwdFingerPrint
from .client.util.Configuration import Configuration
from .client.corelayer.ClientCore import ClientCore
from .client.uilayer.ClientUI import ClientUI

here = path.abspath(path.dirname(__file__))


def main():
    """Main function"""
    MnemopwdFingerPrint().control_fingerprint(prefix=here)
    Configuration.configure()
    if Configuration.action == 'status':
        ClientCore().stop()
    elif Configuration.action == 'start':
        try:
            core = ClientCore()  # The domain layer
            ui = ClientUI(core)  # The UI layer (linked to the domain layer)
            core.add_observer(ui)  # Design pattern Observer to update UI layer

            ui.start()   # Always start the UI layer before the domain layer
            time.sleep(0.1)  # Waiting the UI initialization
            core.start()  # Start domain layer

        except:
            exit()

        else:
            ui.stop()  # Stop UI layer (domain layer stopped by UI layer)
            ui.join()  # Waiting for UI layer
