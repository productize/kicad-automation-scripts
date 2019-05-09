#!/usr/bin/env python
#   Copyright 2015-2016 Scott Bezek and the splitflap contributors
#   Copyright 2019 Productize SPRL
#   Copyright 2019 Seppe Stas
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

import argparse
import logging
import os
import pcbnew
import shutil
import zipfile
from PyPDF2 import PdfFileMerger, PdfFileReader
from collections import namedtuple

import pcb_util

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def plot(pcb, file_format, layers, plot_directory):
    
    temp_dir = os.path.join(plot_directory, 'temp')
    shutil.rmtree(temp_dir, ignore_errors=True)
    try:
        os.makedirs(temp_dir)
        plot_to_directory(pcb, file_format, layers, plot_directory, temp_dir)
    finally:
        # shutil.rmtree(temp_dir, ignore_errors=True)
        pass


def plot_to_directory(pcb, file_format, layers, plot_directory, temp_dir):
    output_files = []

    pcb.set_plot_directory(temp_dir)

    logger.debug(file_format)

    if file_format == 'zip_gerbers':
        # In theory not needed since gerber does not support dril marks, but added just to be sure
        pcb.plot_options.SetDrillMarksType(pcbnew.PCB_PLOT_PARAMS.NO_DRILL_SHAPE)

        for layer in layers:
            logger.debug('plotting layer {} ({}) to Gerber'.format(layer.get_name(), layer.layer_id))
            output_filename = layer.plot(pcbnew.PLOT_FORMAT_GERBER)
            output_files.append(output_filename)

        drill_file = pcb.plot_drill()
        output_files.append(drill_file)

        zip_file_name = os.path.join(plot_directory, '{}_gerbers.zip'.format(pcb.name))
        with zipfile.ZipFile(zip_file_name, 'w') as z:
            for f in output_files:
                z.write(f, os.path.relpath(f, plot_directory))

    elif file_format == 'pdf':
        pcb.plot_options.SetDrillMarksType(pcbnew.PCB_PLOT_PARAMS.FULL_DRILL_SHAPE)
        merger = PdfFileMerger()
        for layer in layers:
            logger.debug('plotting layer {} ({}) to PDF'.format(layer.get_name(), layer.layer_id))
            output_filename = layer.plot(pcbnew.PLOT_FORMAT_PDF)
            output_files.append(output_filename)
            logger.debug(output_filename)
            merger.append(PdfFileReader(file(output_filename, 'rb')), bookmark=layer.get_name())

        drill_map_file = pcb.plot_drill_map()
        if os.path.isfile(drill_map_file): # No drill file is generated if no holes exist
            merger.append(PdfFileReader(file(drill_map_file, 'rb')), bookmark='Drill map')

        merger.write(plot_directory+'/{}.pdf'.format(pcb.name))

    

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Plot a KiCad PCB layout')
    
    parser.add_argument('pcb_file', help='The pcbnew layout (.kicad_pcb) file')
    parser.add_argument('output_dir', help='Output directory')

    parser.add_argument('layers',
        nargs='*',
        help='Names of layers to plot. By default the layers enabled in PCBNew plot menu are plotted'
    )

    parser.add_argument('--file_format', '-f', help='Plot file format',
        choices=['zip_gerbers', 'pdf'],
        default='zip_gerbers'
    )

    args = parser.parse_args()

    pcb = pcb_util.PCB(args.pcb_file)

    if len(args.layers) > 0:
        layers = []
        for layer_name in args.layers:
            layers.append(pcb_util.Layer.from_name(pcb, layer_name))
    else:
        # TODO: figure out why this does not work
        layers = pcb.get_plot_enabled_layers()

    plot(pcb, args.file_format, layers, os.path.abspath(args.output_dir))
