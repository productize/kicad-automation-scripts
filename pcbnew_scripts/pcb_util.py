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
        logger.debug('layer id {} name: {} color: {}'.format(layer_id, pcb.GetLayerName(layer_id), pcb.Colors().GetLayerColor(layer_id).ToU32()))
        layers.append({
            'name': pcb.GetLayerName(layer_id),
            'color': pcb.Colors().GetLayerColor(layer_id).ToU32(),
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
