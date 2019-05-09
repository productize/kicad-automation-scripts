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

import datetime
import logging
import os
import pcbnew
import subprocess

from contextlib import contextmanager

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Layer(object):
    def __init__(self, pcb, layer_id):
        self.pcb = pcb
        self.layer_id = layer_id

    @staticmethod 
    def from_name(pcb, layer_name):
        return Layer(pcb, pcb.get_layer_id(layer_name))

    def get_color(self):
        return self.pcb.get_layer_color(self.layer_id)

    def get_name(self):
        return self.pcb.get_layer_name(self.layer_id)

    def plot(self, plot_format):
        plot_controller = self.pcb.plot_controller
        plot_controller.SetLayer(self.layer_id)
        plot_controller.OpenPlotfile(self.get_name(), plot_format , 'Plot')
        output_filename = plot_controller.GetPlotFileName()
        plot_controller.PlotLayer()
        plot_controller.ClosePlot()
        return output_filename

class PCB(object):
    def __init__(self, board_file):
        self.name = os.path.splitext(os.path.basename(board_file))[0]
        self.board = pcbnew.LoadBoard(board_file)
        self.plot_controller = pcbnew.PLOT_CONTROLLER(self.board)
        self.plot_options = self.plot_controller.GetPlotOptions()

        self.plot_options.SetPlotFrameRef(False)
        self.plot_options.SetLineWidth(pcbnew.FromMM(0.35))
        self.plot_options.SetScale(1)
        self.plot_options.SetUseAuxOrigin(True)
        self.plot_options.SetMirror(False)
        self.plot_options.SetExcludeEdgeLayer(False)
        self.plot_controller.SetColorMode(True);

    def set_plot_directory(self, plot_directory):
        self.plot_directory = plot_directory
        self.plot_options.SetOutputDirectory(plot_directory)


    def plot_drill(self):
        board_name = os.path.splitext(os.path.basename(self.board.GetFileName()))[0]
        logger.info('Plotting drill file')
        drill_writer = pcbnew.EXCELLON_WRITER(self.board)

        mirror = False
        minimalHeader = False
        offset = pcbnew.wxPoint(0, 0)
        merge_npth = True # TODO: do we want this?
        drill_writer.SetOptions(mirror, minimalHeader, offset, merge_npth)

        metric_format = True
        drill_writer.SetFormat(metric_format)

        generate_drill = True
        generate_map = False
        drill_writer.CreateDrillandMapFilesSet(self.plot_directory, generate_drill, generate_map)

        drill_file_name = os.path.join(
            self.plot_directory,
            '%s.drl' % (board_name,)
        )

        return drill_file_name

    def plot_drill_map(self):
        board_name = os.path.splitext(os.path.basename(self.board.GetFileName()))[0]
        drill_writer = pcbnew.EXCELLON_WRITER(self.board)
        drill_writer.SetMapFileFormat(pcbnew.PLOT_FORMAT_PDF)

        mirror = False
        minimalHeader = False
        offset = pcbnew.wxPoint(0, 0)
        merge_npth = True # TODO: do we want this?
        drill_writer.SetOptions(mirror, minimalHeader, offset, merge_npth)

        metric_format = True
        drill_writer.SetFormat(metric_format)

        generate_drill = False
        generate_map = True
        drill_writer.CreateDrillandMapFilesSet(self.plot_directory, generate_drill, generate_map)

        map_file_name = os.path.join(
            self.plot_directory,
            '%s-drl_map.pdf' % (board_name,)
        )

        return map_file_name

    def get_enabled_layers(self):
        stack = self.board.GetEnabledLayers().UIOrder();

        layers = []
        for layer_id in stack:
            layers.append(Layer(self, layer_id))
        return layers

    def get_plot_enabled_layers(self):
        stack = self.board.GetPlotOptions().GetLayerSelection().UIOrder();

        layers = []
        for layer_id in stack:
            layers.append(Layer(self, layer_id))
        return layers

    def get_layer_color(self, layer_id):
        return self.board.Colors().GetLayerColor(layer_id).ToU32()

    def get_layer_name(self, layer_id):
        return self.board.GetLayerName(layer_id)

    def get_layer_id(self, layer_name):
        return self.board.GetLayerID(layer_name)
