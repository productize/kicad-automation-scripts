#!/usr/bin/env python

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
import time

from contextlib import contextmanager

eeschema_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(eeschema_dir)

sys.path.append(repo_root)

from util import file_util
from export_util import (
    PopenContext,
    xdotool,
    wait_for_window,
    recorded_xvfb,
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def eeschema_plot_schematic(output_directory):
    # The "Not Found" window pops up if libraries required by the schematic have
    # not been found. This can be ignored as all symbols are placed inside the
    # *-cache.lib file:
    try:
        nf_title = 'Not Found'
        wait_for_window(nf_title, nf_title, 3)

        logger.info('Dismiss eeschema library warning window')
        xdotool(['search', '--name', nf_title, 'windowfocus'])
        xdotool(['key', 'KP_Enter'])
    except RuntimeError:
        pass

    wait_for_window('eeschema', '\[')

    logger.info('Focus main eeschema window')
    xdotool(['search', '--name', '\[', 'windowfocus'])

    logger.info('Open File->Plot->Plot')
    xdotool(['key', 'alt+f'])
    xdotool(['key', 'p'])
    xdotool(['key', 'p'])

    wait_for_window('plot', 'Plot')
    xdotool(['search', '--name', 'Plot', 'windowfocus'])

    logger.info('Enter build output directory')
    xdotool(['type', output_directory])

    logger.info('Select PDF plot format')
    xdotool([
        'key',
        'Tab',
        'Tab',
        'Tab',
        'Tab',
        'Tab',
        'Up',
        'Up',
        'Up',
        'space',
    ])

    logger.info('Plot')
    xdotool(['key', 'Return'])

    logger.info('Wait before shutdown')
    time.sleep(2)

def export_schematic(schematic):
    schematic_file = os.path.join(eeschema_dir, schematic)
    output_dir = os.path.join(eeschema_dir, 'build')
    file_util.mkdir_p(output_dir)

    screencast_output_file = os.path.join(output_dir, 'export_schematic_screencast.ogv')
    schematic_output_pdf_file = os.path.join(output_dir, 'schematic.pdf')
    schematic_output_png_file = os.path.join(output_dir, 'schematic.png')

    with recorded_xvfb(screencast_output_file, width=800, height=600, colordepth=24):
        with PopenContext(['eeschema', schematic_file], close_fds=True) as eeschema_proc:
            eeschema_plot_schematic(output_dir)
            eeschema_proc.terminate()
    
if __name__ == '__main__':
    export_schematic(sys.argv[1])

