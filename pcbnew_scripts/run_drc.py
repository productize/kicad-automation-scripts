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

def parse_drc(drc_file):
    from re import search as regex_search

    with open(drc_file, 'r') as f:
        lines = f.read().splitlines()

    drc_errors = None
    unconnected_pads = None

    for line in lines:
        if drc_errors != None and unconnected_pads != None:
            break;
        m = regex_search(
            '^\*\* Found ([0-9]+) DRC errors \*\*$', line)
        if m != None:
            drc_errors = m.group(1);
            continue
        m = regex_search(
            '^\*\* Found ([0-9]+) unconnected pads \*\*$', line)
        if m != None:
            unconnected_pads = m.group(1);
            continue

    return {
        'drc_errors': int(drc_errors),
        'unconnected_pads': int(unconnected_pads)
    }


def run_drc(pcb_file, output_dir, record=True):

    file_util.mkdir_p(output_dir)

    recording_file = os.path.join(output_dir, 'run_drc_screencast.ogv')
    drc_output_file = os.path.join(os.path.abspath(output_dir), 'drc_result.rpt')

    xvfb_kwargs = {
	    'width': 800,
	    'height': 600,
	    'colordepth': 24,
    }

    with recorded_xvfb(recording_file, **xvfb_kwargs) if record else Xvfb(**xvfb_kwargs):
        with PopenContext(['pcbnew', pcb_file], close_fds=True) as pcbnew_proc:
            clipboard_store(drc_output_file)

            window = wait_for_window('pcbnew', 'Pcbnew', 10, False)

            logger.info('Focus main pcbnew window')
            wait_for_window('pcbnew', 'Pcbnew')

            # Needed to rebuild the menu, making sure it is actually built
            xdotool(['windowsize', '--sync', window, '750', '600'])

            wait_for_window('pcbnew', 'Pcbnew')

            logger.info('Open Inspect->DRC')
            xdotool(['key', 'alt+i', 'd'])

            logger.info('Focus DRC modal window')
            wait_for_window('DRC modal window', 'DRC Control')
            xdotool(['key',
                'Tab',
                'Tab',
                'Tab', # Refill zones on DRC gets saved in /root/.config/kicad/pcbnew as RefillZonesBeforeDrc
                'key',
                'Tab',
                'space', # Enable reporting all errors for tracks
                'Tab',
                'Tab',
                'Tab',
                'space',
                'Tab'
            ])
            logger.info('Pasting output dir')
            xdotool(['key', 'ctrl+v'])

            xdotool(['key', 'Return'])

            wait_for_window('Report completed dialog', 'Disk File Report Completed')
            xdotool(['key', 'Return'])
            pcbnew_proc.terminate()

    return drc_output_file

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='KiCad automated DRC runner')

    parser.add_argument('kicad_pcb_file', help='KiCad schematic file')
    parser.add_argument('output_dir', help='Output directory')
    parser.add_argument('--ignore_unconnected', '-i', help='Ignore unconnected paths',
        action='store_true'
    )
    parser.add_argument('--record', help='Record the UI automation',
        action='store_true'
    )

    args = parser.parse_args()

    drc_result = parse_drc(run_drc(args.kicad_pcb_file, args.output_dir, args.record))

    logging.info(drc_result);
    if drc_result['drc_errors'] == 0 and drc_result['unconnected_pads'] == 0:
        exit(0)
    else:

        logger.error('Found {} DRC errors and {} unconnected pads'.format(
            drc_result['drc_errors'],
            drc_result['unconnected_pads']
        ))
        exit(drc_result['drc_errors']+drc_result['unconnected_pads'])
    
