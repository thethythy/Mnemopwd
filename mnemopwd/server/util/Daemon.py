# -*- coding: utf-8 -*-

# Copyright (c) 2015, Thierry Lemeunier <thierry at lemeunier dot net>
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

"""
Provides a simple Daemon class to ease the process of forking a
python application on POSIX systems.
"""

import errno
import logging
import socket
from logging.handlers import RotatingFileHandler
import os
import signal
import sys
import time
import datetime

from ...server.util.Configuration import Configuration


class Daemon(object):
    """Daemon base class"""

    def run(self):
        """Override. We are in the daemon at this point."""

    def main(self):
        """Read the command line and either start or stop the daemon"""
        if Configuration.action == 'start':
            self.start()
        elif Configuration.action == 'stop':
            self.stop()
        elif Configuration.action == 'status':
            self.status()
        else:
            raise ValueError(Configuration.action)

    def on_sigterm(self, signalnum, frame):
        """Handle segterm by treating as a keyboard interrupt"""
        raise KeyboardInterrupt('SIGTERM')

    def add_signal_handlers(self):
        """Register the sigterm handler"""
        signal.signal(signal.SIGTERM, self.on_sigterm)

    def start(self):
        """Initialize and run the daemon"""
        self.check_pid()
        self.add_signal_handlers()
        self.start_logging()

        try:
            self.check_pid_writable()
            self.check_server_accessibility()
            self.daemonize()
        except:
            logging.exception("failed to start due to an exception")
            raise

        self.write_pid()
        try:
            try:
                self.run()
            except (KeyboardInterrupt, SystemExit):
                pass
            except OSError as exc:
                logging.exception(str(exc))
                pass
            except:
                logging.exception("stopping with an exception")
                raise
        finally:
            self.remove_pid()

    def stop(self):
        """Stop the running process"""
        if Configuration.pidfile and os.path.exists(Configuration.pidfile):
            file = open(Configuration.pidfile)
            pid = int(file.read())
            file.close()
            os.kill(pid, signal.SIGTERM)
            for n in range(10):
                time.sleep(0.25)
                try:
                    os.kill(pid, 0)
                except OSError as why:
                    if why.errno == errno.ESRCH:
                        break
                    else:
                        raise
            else:
                sys.exit("pid %d did not die" % pid)
        else:
            sys.exit("not running")
            
    def status(self):
        self.check_pid(True)

    def start_logging(self):
        """Configure the logging module"""
        handler = RotatingFileHandler(
            Configuration.logfile,
            maxBytes=Configuration.logmaxmb * 1024 * 1024,
            backupCount=Configuration.logbackups)
        log = logging.getLogger()
        log.setLevel(Configuration.loglevel)
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        log.addHandler(handler)

    def check_pid(self, status=False):
        """Check the pid file.

        Stop using sys.exit() if another instance is already running.
        If the pid file exists but no other instance is running,
        delete the pid file.
        """
        if not Configuration.pidfile:
            return
        if os.path.exists(Configuration.pidfile):
            try:
                pid = int(open(Configuration.pidfile, 'rb').read().decode('utf-8').strip())
            except ValueError:
                msg = 'pidfile %s contains a non-integer value' % Configuration.pidfile
                sys.exit(msg)
            try:
                os.kill(pid, 0)
            except OSError as err:
                if err.errno == errno.ESRCH:
                    # The pid doesn't exist, so remove the stale pidfile.
                    os.remove(Configuration.pidfile)
                else:
                    msg = ("failed to check status of process %s "
                           "from pidfile %s: %s" % (pid, Configuration.pidfile, err.strerror))
                    sys.exit(msg)
            else:
                mtime = os.stat(Configuration.pidfile).st_mtime
                since = datetime.timedelta(seconds=(time.time() - mtime))
                msg = 'instance [pid %s] seems to be running since %s [%s days]' % (pid, time.ctime(mtime), since.days)
                sys.exit(msg)
        elif status:
            print('no instance seems to be running')

    def check_pid_writable(self):
        """Verify the user has access to write to the pid file.

        Note that the eventual process ID isn't known until after
        daemonize(), so it's not possible to write the PID here.
        """
        if not Configuration.pidfile:
            return
        if os.path.exists(Configuration.pidfile):
            check = Configuration.pidfile
        else:
            check = os.path.dirname(Configuration.pidfile)
        if not os.access(check, os.W_OK):
            msg = 'unable to write to pidfile %s' % Configuration.pidfile
            sys.exit(msg)

    def check_server_accessibility(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((Configuration.host, Configuration.port))
        except OSError as exc:
            if exc.errno == 48:
                print("address [%s:%d] already in use" % (Configuration.host, Configuration.port))
                sys.exit(1)

    def write_pid(self):
        """Write to the pid file"""
        if Configuration.pidfile:
            open(Configuration.pidfile, 'wb').write(str(os.getpid()).encode('utf-8'))

    def remove_pid(self):
        """Delete the pid file"""
        if Configuration.pidfile and os.path.exists(Configuration.pidfile):
            os.remove(Configuration.pidfile)

    def daemonize(self):
        """Detach from the terminal and continue as a daemon"""
        if os.fork():   # launch child and...
            os._exit(0)  # kill off parent
        os.setsid()
        if os.fork():   # launch child and...
            os._exit(0)  # kill off parent again.
        os.umask(63)  # 077 in octal
        null = os.open('/dev/null', os.O_RDWR)
        for i in range(3):
            try:
                os.dup2(null, i)
            except OSError as e:
                if e.errno != errno.EBADF:
                    raise
        os.close(null)
