import unittest
from mockito import when
from unittest.mock import MagicMock

import toga
import matplotlib.pyplot as plt

import conversationalspacemapapp.Types.Data as Data
import conversationalspacemapapp.Plotter.PlotMap as PlotMap
import conversationalspacemapapp.Types.Constants as Constants
import conversationalspacemapapp.Parser.TimestampParser as TranscriptParser


class TestPlotMap(unittest.TestCase):
    parser: TranscriptParser.AbstractParser
    fig: plt.figure()
    ax: plt.Axes
    app: toga.App

    def setUp(self):
        TestPlotMap.parser = MagicMock()
        TestPlotMap.parser.map = [
            Data.Utterance(number=1, speaker="SPEAKER_00", words=10),
            Data.Utterance(number=2, speaker="SPEAKER_01", words=15),
        ]
        TestPlotMap.app = MagicMock()
        when(TestPlotMap.app)._get_participant_role("SPEAKER_00").thenReturn(
            Constants.Participant.Interviewer
        )
        when(TestPlotMap.app)._get_participant_role("SPEAKER_01").thenReturn(
            Constants.Participant.Interviewee
        )
        when(TestPlotMap.app)._get_participant_color("SPEAKER_00").thenReturn(
            PlotMap.MapBarPlot.COLORS[0]
        )
        when(TestPlotMap.app)._get_participant_color("SPEAKER_01").thenReturn(
            PlotMap.MapBarPlot.COLORS[1]
        )
        TestPlotMap.fig, TestPlotMap.ax = plt.subplots()

    def tearDown(self):
        TestPlotMap.fig.show()

    def test_bar_plot(self):
        plotter = PlotMap.MapBarPlot(
            parser=TestPlotMap.parser,
            ax=TestPlotMap.ax,
            fig=TestPlotMap.fig,
            app=TestPlotMap.app,
        )
        self.assertEqual(TestPlotMap.parser.map[0].words, 10)
        plotter.plot("I01")
