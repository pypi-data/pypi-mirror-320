"""
Generate conversational space maps for interview data.
"""

import toga
from toga.style import Pack
from toga.constants import COLUMN
import toga_chart
import pathlib
import platform
from typing import Callable

import conversationalspacemapapp.Parser.TimestampParser as TranscriptParser
import conversationalspacemapapp.Plotter.PlotMap as PlotMap
import conversationalspacemapapp.Types.Constants as Constants


class ConversationalSpaceMapApp(toga.App):
    default_padding = 5
    default_flex = 1
    save_file_formats = ["PDF", "PNG", "SVG"]

    @property
    def is_not_empty_file_selection(self):
        return len(self.path_input.items) > 0

    @property
    def _has_parser(self):
        return self.parser is not None

    def startup(self):
        self.parser: TranscriptParser.AbstractParser = None
        self.map = None
        self.plot_title = ""

        home = self.create_home_layout()
        transcript = self.create_transcript_layout()
        about = self.create_about_layout()

        main = toga.OptionContainer(
            content=[("Home", home), ("Transcript", transcript), ("About", about)]
        )
        main.style.padding = ConversationalSpaceMapApp.default_padding
        self.set_background(main)

        self.main_window = toga.MainWindow()
        self.main_window.content = main
        self.main_window.size = toga.Size(width=1300, height=1000)
        self.main_window.show()

    def create_about_layout(self):
        # Create app description page
        description = toga.WebView(
            url="https://manuelbieri.ch/ConversationalSpaceMapApp/"
        )
        description.style.padding = ConversationalSpaceMapApp.default_padding
        description.style.flex = ConversationalSpaceMapApp.default_flex
        self.set_background(description)
        about = toga.Box(
            children=[description],
            style=Pack(direction=COLUMN),
        )
        return about

    def create_transcript_layout(self):
        self.transcript = toga.MultilineTextInput()
        self.transcript.style.padding = ConversationalSpaceMapApp.default_padding
        if self._has_parser:
            self.transcript.value = self.parser.content
        else:
            self.transcript.enabled = False
        return self.transcript

    def create_home_layout(self):
        # Create plot settings layout
        plot_settings = self.create_plot_settings_layout()
        # Create participants layout
        self.plot_participants = toga.Box(
            children=[
                toga.Label(
                    "Participants:",
                    style=Pack(padding=ConversationalSpaceMapApp.default_padding),
                )
            ]
        )
        # Create labels
        self.label = toga.Label("")
        self.label.style.padding = ConversationalSpaceMapApp.default_padding
        # Create chart
        self.chart = toga_chart.Chart(style=Pack(flex=1), on_draw=self.draw_chart)
        self.chart.style.padding = ConversationalSpaceMapApp.default_padding
        self.chart.style.flex = ConversationalSpaceMapApp.default_flex

        # Assemble home layout
        home = toga.Box(
            children=[plot_settings, self.plot_participants, self.label, self.chart],
            style=Pack(direction=COLUMN),
        )
        self._set_parser()
        return home

    def create_plot_settings_layout(self):
        # Create selections
        self.file_format = toga.Selection(
            items=ConversationalSpaceMapApp.save_file_formats
        )
        self.file_format.style.padding = ConversationalSpaceMapApp.default_padding
        self.file_format.style.flex = ConversationalSpaceMapApp.default_flex
        self.path_input = toga.Selection(
            items=self._get_file_history(), on_change=self._set_file
        )
        self.path_input.style.padding = ConversationalSpaceMapApp.default_padding
        self.path_input.readonly = True
        self.path_input.style.flex = 10

        # Create buttons
        self.button = self.button_factory("📄", on_press=self.open_handler)
        self.plot = self.button_factory(
            "🖌", on_press=self.plot_handler, enabled=self.is_not_empty_file_selection
        )
        self.save = self.button_factory("💾", on_press=self.save_handler, enabled=False)
        plot_settings = toga.Box(
            children=[
                self.path_input,
                self.button,
                self.plot,
                self.file_format,
                self.save,
            ]
        )
        return plot_settings

    def set_plot_participants_layout(self):
        assert self.path_input is not None
        self.plot_participants.clear()
        for participant in self.parser.participants:
            self.plot_participants.add(
                self.get_participant_settings_layout(participant)
            )

    def get_participant_settings_layout(self, participant: str) -> toga.Box:
        # Create participant label
        label = toga.Label(participant)
        label.style.padding = ConversationalSpaceMapApp.default_padding
        label.style.flex = ConversationalSpaceMapApp.default_flex

        # Create participant role
        role = toga.Selection(
            items=Constants.Participant,
            id=participant + "_role",
            on_change=self.plot_handler,
        )
        role.style.padding = ConversationalSpaceMapApp.default_padding
        role.style.flex = ConversationalSpaceMapApp.default_flex

        # Create color picker
        color = toga.Selection(
            items=PlotMap.MapBarPlot.COLORS,
            id=participant + "_color",
            on_change=self.plot_handler,
        )
        color.style.padding = ConversationalSpaceMapApp.default_padding
        color.style.flex = ConversationalSpaceMapApp.default_flex

        return toga.Box(children=[label, role, color])

    def draw_chart(self, chart, figure, *args, **kwargs):
        if self.parser is not None:
            figure.clf()
            # Add a subplot that is a histogram of the data, using the normal matplotlib API
            ax = figure.add_subplot(1, 1, 1)

            self.map = PlotMap.MapBarPlot(
                parser=self.parser, ax=ax, fig=figure, app=self
            )
            self.map.plot(title=self.plot_title)
            figure.tight_layout()
        else:
            return

    def button_factory(
        self,
        label: str,
        on_press: Callable,
        enabled: bool = True,
        padding: int = None,
        flex: int = None,
    ) -> toga.Button:
        button = toga.Button(label, on_press=on_press)
        button.enabled = enabled
        button.style.padding = (
            ConversationalSpaceMapApp.default_padding if padding is None else padding
        )
        button.style.flex = (
            ConversationalSpaceMapApp.default_flex if padding is None else flex
        )
        return button

    @staticmethod
    def set_background(widget: toga.Widget):
        if "macOS" in platform.platform():
            widget.style.background_color = "transparent"

    async def open_handler(self, widget):
        file = toga.OpenFileDialog("Open file", file_types=["txt"])
        path = await self.main_window.dialog(file)
        if path is not None:
            try:
                self.path_input.value = path
            except ValueError:
                self.path_input.items.append(path)
                self.path_input.value = path
                self._write_file_history()
            self._set_file(widget)
        else:
            return

    def _set_file(self, widget):
        if self.path_input.value.is_file():
            self.plot_title = self.path_input.value.stem
            self.plot.enabled = True
            self._set_parser()
        else:
            Exception("File not valid: " + self.path_input.value.as_posix())

    def _write_file_history(self):
        history = pathlib.Path(__file__).parent / "assets" / "history.txt"
        content = str(self.path_input.value)
        if history.is_file() and len(content.strip()) != 0:
            with open(history, "a") as f:
                f.write(content + "\n")

    def plot_handler(self, widget):
        assert self.is_not_empty_file_selection
        if self.parser is None:
            self._set_parser()
        self.chart.redraw()
        self.save.enabled = True
        self._set_label(widget)

    async def save_handler(self, widget):
        if self.path_input.value is not None:
            file = toga.SaveFileDialog(
                "Save file",
                suggested_filename=str(pathlib.Path(self.path_input.value).stem),
                file_types=ConversationalSpaceMapApp.save_file_formats,
            )
            path = await self.main_window.dialog(file)
            if path is not None:
                self.map.save(path)
            else:
                return
        else:
            return

    def _set_label(self, widget=None):
        total_words = sum(utterance.words for utterance in self.parser.map)
        text = f"Total words: {total_words} / "
        for participant in self.parser.participants:
            participant_words = sum(
                utterance.words if participant == utterance.speaker else 0
                for utterance in self.parser.map
            )
            text += f"Words {participant}: {participant_words} ({round(100 * participant_words / total_words, ndigits=1)}%) / "
        text += f"Total utterances: {len(self.parser.map)}"
        self.label.text = text
        self.label.refresh()

    def _set_parser(self):
        if self.is_not_empty_file_selection:
            self.parser = TranscriptParser.TimestampParser(self.path_input.value)
            self.set_plot_participants_layout()
            self._set_label()
            try:
                self.transcript.value = self.parser.content
            except AttributeError:
                print("No attribute")

    def _get_file_history(self) -> [pathlib.Path]:
        history = pathlib.Path(__file__).parent / "assets" / "history.txt"
        if history.is_file():
            with open(history, "r") as f:
                output = []
                files = sorted(f.readlines())
                for file in files:
                    file = file.strip("\n")
                    file = pathlib.Path(file)
                    if file.is_file():
                        output.append(file)
                return output
        else:
            return []

    def get_participant_role(self, speaker_name: str) -> Constants.Participant:
        role_key = speaker_name + "_role"
        if (
            speaker_name in self.parser.participants
            and role_key in self.app.widgets.keys()
        ):
            return self.app.widgets[speaker_name + "_role"].value
        return Constants.Participant.Undefined

    def get_participant_color(self, speaker_name: str) -> str:
        color_key = speaker_name + "_color"
        if (
            speaker_name in self.parser.participants
            and color_key in self.app.widgets.keys()
        ):
            return self.app.widgets[speaker_name + "_color"].value
        return None


def main():
    return ConversationalSpaceMapApp(
        "Conversational Space Map App",
        "ch.manuelbieri.conversationalspacemapapp",
        icon="assets/conversationalspacemapapp.png",
    )
