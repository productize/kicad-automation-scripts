#!/usr/bin/env python
#
# Utility functions for UI automation with xdotool in a virtual framebuffer
# with XVFB. Also includes utilities for accessing the clipboard for easily
# and efficiently copy-pasting strings in the UI
# Based on splitflap/electronics/scripts/export_util.py by Scott Bezek
#
#   Copyright 2019 Productize SPRL
#   Copyright 2015-2016 Scott Bezek and the splitflap contributors
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import logging
import os
import subprocess
import sys
import tempfile
import time

from contextlib import contextmanager

from xvfbwrapper import Xvfb
from util import file_util

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class PopenContext(subprocess.Popen):
    def __enter__(self):
        return self
    def __exit__(self, type, value, traceback):
        if self.stdout:
            self.stdout.close()
        if self.stderr:
            self.stderr.close()
        if self.stdin:
            self.stdin.close()
        if type:
            self.terminate()
        # Wait for the process to terminate, to avoid zombies.
        self.wait()

@contextmanager
def recorded_xvfb(video_filename, **xvfb_args):
    with Xvfb(**xvfb_args):
        with PopenContext([
                'recordmydesktop',
                '--no-sound',
                '--no-frame',
                '--on-the-fly-encoding',
                '-o', video_filename], close_fds=True) as screencast_proc: 
            yield
            screencast_proc.terminate()


def xdotool(command):
    return subprocess.check_output(['xdotool'] + command)

def clipboard_store(string):
    p = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE)
    outs, errs = p.communicate(input=string)
    if (errs):
        logger.error('Failed to store string in clipboard')
        logger.error(errs)

def clipboard_retrieve():
    p = subprocess.Popen(['xclip', '-o', '-selection', 'clipboard'], stdout=subprocess.PIPE)
    output = '';
    for line in p.stdout:
        output += line.decode()
    return output;

def wait_for_window(name, window_regex, timeout=10, focus=True):
    DELAY = 0.5
    logger.info('Waiting for %s window...', name)
    xdotool_command = ['search', '--onlyvisible', '--name', window_regex]
    if focus:
        xdotool_command.append('windowfocus')

    for i in range(int(timeout/DELAY)):
        try:
            window_id = xdotool(xdotool_command).strip()
            logger.info('Found %s window', name)
            logger.debug('Window id: %s', window_id)
            return window_id
        except subprocess.CalledProcessError:
            pass
        time.sleep(DELAY)
    raise RuntimeError('Timed out waiting for %s window' % name)
