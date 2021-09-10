#!/usr/bin/env python
#
#   UI automation script to run DRC on a KiCad PCBNew layout
#   Sadly it is not possible to run DRC with the PCBNew Python API since the
#   code is to tied in to the UI. Might change in the future.
#
#   Copyright 2019 Productize SPRL
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

import sys
import os
import logging
import argparse
import time
from xvfbwrapper import Xvfb

pcbnew_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(pcbnew_dir)

sys.path.append(repo_root)

from util import file_util
from util.ui_automation import (
    PopenContext,
    xdotool,
    wait_for_window,
    recorded_xvfb,
    clipboard_store
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def run_export(pcb_file, output_file, record=True):

    recording_file = os.path.join('/tmp', 'export_dsn_screencast.ogv')
    dsn_output_file = os.path.abspath(output_file)

    if os.path.exists(dsn_output_file):
        logger.error('DSN file already exists')
        exit(-1)

    xvfb_kwargs = {
	    'width': 800,
	    'height': 600,
	    'colordepth': 24,
    }

    with recorded_xvfb(recording_file, **xvfb_kwargs) if record else Xvfb(**xvfb_kwargs):
        with PopenContext(['pcbnew', pcb_file], close_fds=True) as pcbnew_proc:
            clipboard_store(dsn_output_file)

            window = wait_for_window('pcbnew', 'Pcbnew', 10, False)

            logger.info('Focus main pcbnew window')
            wait_for_window('pcbnew', 'Pcbnew')

            # Needed to rebuild the menu, making sure it is actually built
            xdotool(['windowsize', '--sync', window, '750', '600'])

            wait_for_window('pcbnew', 'Pcbnew')

            logger.info('File Menu')
            xdotool(['key', 'alt+f', 'x', 'Return'])

            logger.info('Focus Export modal window')
            wait_for_window('Save', 'Specctra DSN File')

            logger.info('Pasting output file')
            xdotool(['key', 'ctrl+a', 'ctrl+v', 'Return'])

            # give the app some time to serialize
            time.sleep(2)
            pcbnew_proc.terminate()

    return dsn_output_file

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='KiCad automated DRC runner')

    parser.add_argument('kicad_pcb_file', help='KiCad layout file')
    parser.add_argument('output_file', help='Output file')
    parser.add_argument('--record', help='Record the UI automation',
        action='store_true'
    )

    args = parser.parse_args()

    export_result = run_export(args.kicad_pcb_file, args.output_file, args.record)

    logging.info(export_result);
