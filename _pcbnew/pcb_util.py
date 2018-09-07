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

import datetime
import logging
import os
import pcbnew
import subprocess

from contextlib import contextmanager

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# TODO: figure out how to index pcbnew.g_ColorRefs
# I gave up, copied from colors.cpp
_COLOR = {
    pcbnew.BLACK:        [0,    0,   0],
    pcbnew.DARKDARKGRAY: [72,   72,  72],
    pcbnew.DARKGRAY:     [132,  132, 132],
    pcbnew.LIGHTGRAY:    [194,  194, 194],
    pcbnew.WHITE:        [255,  255, 255],
    pcbnew.LIGHTYELLOW:  [194,  255, 255],
    pcbnew.DARKBLUE:     [72,   0,   0],
    pcbnew.DARKGREEN:    [0,    72,  0],
    pcbnew.DARKCYAN:     [72,   72,  0],
    pcbnew.DARKRED:      [0,    0,   72],
    pcbnew.DARKMAGENTA:  [72,   0,   72],
    pcbnew.DARKBROWN:    [0,    72,  72],
    pcbnew.BLUE:         [132,  0,   0],
    pcbnew.GREEN:        [0,    132, 0],
    pcbnew.CYAN:         [132,  132, 0],
    pcbnew.RED:          [0,    0,   132],
    pcbnew.MAGENTA:      [132,  0,   132],
    pcbnew.BROWN:        [0,    132, 132],
    pcbnew.LIGHTBLUE:    [194,  0,   0],
    pcbnew.LIGHTGREEN:   [0,    194, 0],
    pcbnew.LIGHTCYAN:    [194,  194, 0],
    pcbnew.LIGHTRED:     [0,    0,   194],
    pcbnew.LIGHTMAGENTA: [194,  0,   194],
    pcbnew.YELLOW:       [0,    194, 194],
    pcbnew.PUREBLUE:     [255,  0,   0],
    pcbnew.PUREGREEN:    [0,    255, 0],
    pcbnew.PURECYAN:     [255,  255, 0],
    pcbnew.PURERED:      [0,    0,   255],
    pcbnew.PUREMAGENTA:  [255,  0,   255],
    pcbnew.PUREYELLOW:   [0,    255, 255]
}

def open_board(pcb_filename):
    return pcbnew.LoadBoard(pcb_filename)

def layer_from_name(pcb, layer_name):
    return pcb.GetLayerID(layer_name)

def get_layer_name(pcb, layer_id):
    return pcb.GetLayerName(layer_id)

@contextmanager
def get_plotter(pcb_filename, build_directory):
    yield GerberPlotter(pcbnew.LoadBoard(pcb_filename), build_directory)

def get_layers(pcb_filename):
    pcb = pcbnew.LoadBoard(pcb_filename)
    stack = pcb.GetEnabledLayers().UIOrder();

    layers = []
    for layer_id in stack:
        print pcb.GetLayerName(layer_id)
        layers.append({
            'name': pcb.GetLayerName(layer_id),
            'color': _COLOR[pcbnew.ColorGetBase(pcb.GetLayerColor(layer_id))],
            'visible': pcb.IsLayerVisible(layer_id)
        })
    return layers

class GerberPlotter(object):
    def __init__(self, board, build_directory):
        self.board = board
        self.build_directory = build_directory
        self.plot_controller = pcbnew.PLOT_CONTROLLER(board)
        self.plot_options = self.plot_controller.GetPlotOptions()
        self.plot_options.SetOutputDirectory(build_directory)

        self.plot_options.SetPlotFrameRef(False)
        self.plot_options.SetLineWidth(pcbnew.FromMM(0.35))
        self.plot_options.SetScale(1)
        self.plot_options.SetUseAuxOrigin(True)
        self.plot_options.SetMirror(False)
        self.plot_options.SetExcludeEdgeLayer(False)
        self.plot_controller.SetColorMode(True);

    def plot(self, layer, plot_format):
        layer_name = get_layer_name(self.board, layer)
        logger.info('Plotting layer %s (kicad layer=%r)', layer_name, layer)
        self.plot_controller.SetLayer(layer)
        self.plot_controller.OpenPlotfile(layer_name, plot_format , 'Plot')
        output_filename = self.plot_controller.GetPlotFileName()
        self.plot_controller.PlotLayer()
        self.plot_controller.ClosePlot()
        return output_filename

    def plot_drill(self):
        board_name = os.path.splitext(os.path.basename(self.board.GetFileName()))[0]
        logger.info('Plotting drill file')
        drill_writer = pcbnew.EXCELLON_WRITER(self.board)
        drill_writer.SetMapFileFormat(pcbnew.PLOT_FORMAT_PDF)

        mirror = False
        minimalHeader = False
        offset = pcbnew.wxPoint(0, 0)
        merge_npth = True
        drill_writer.SetOptions(mirror, minimalHeader, offset, merge_npth)

        metric_format = True
        drill_writer.SetFormat(metric_format)

        generate_drill = True
        generate_map = True
        drill_writer.CreateDrillandMapFilesSet(self.build_directory, generate_drill, generate_map)

        drill_file_name = os.path.join(
            self.build_directory,
            '%s.drl' % (board_name,)
        )

        map_file_name = os.path.join(
            self.build_directory,
            '%s-drl_map.pdf' % (board_name,)
        )
        return drill_file_name, map_file_name
