import toga
import toga_chart
from toga.style import Pack
from toga.constants import COLUMN

import pathlib
import platform
from typing import Callable

import conversationalspacemapapp.Plotter.PlotMap as PlotMap
import conversationalspacemapapp.Types.Constants as Constants
import conversationalspacemapapp.App.AbstractApp as AbstractApp


class ConversationalSpaceMapAppToga(AbstractApp.AbstractApp, toga.App):
    default_padding = 5
    default_flex = 1

    def __init__(self, name, id):
        super(ConversationalSpaceMapAppToga, self).__init__(formal_name=name, app_id=id)

    @property
    def path(self) -> pathlib.Path | None:
        return self.path_input.value

    @property
    def has_path(self):
        return self.path is not None and self.path.is_file()

    @property
    def has_parser(self):
        return self.parser is not None

    def startup(self):
        self._create_window()

    def _set_window(self, tab_menu):
        self.main_window = toga.MainWindow()
        self.main_window.content = tab_menu
        self.main_window.size = toga.Size(width=1300, height=1000)
        self.main_window.show()

    def _create_tab_menu(self, tabs):
        main = toga.OptionContainer(content=tabs)
        main.style.padding = ConversationalSpaceMapAppToga.default_padding
        self._set_transparent_background(main)
        return main

    def _create_about_layout(self):
        # Create app description page
        description = toga.WebView(
            url="https://manuelbieri.ch/ConversationalSpaceMapApp/"
        )
        description.style.padding = ConversationalSpaceMapAppToga.default_padding
        description.style.flex = ConversationalSpaceMapAppToga.default_flex
        self._set_transparent_background(description)
        about = toga.Box(
            children=[description],
            style=Pack(direction=COLUMN),
        )
        return about

    def _create_transcript_layout(self):
        self.transcript = toga.MultilineTextInput()
        self.transcript.style.padding = ConversationalSpaceMapAppToga.default_padding
        if self.has_parser:
            self.transcript.value = self.parser.content
        else:
            self.transcript.enabled = False
        return self.transcript

    def _set_transcript(self, content: str):
        assert type(content) == str
        self.transcript.value = content

    def _set_home_window(self, plot_settings, participants, label, chart):
        assert plot_settings is not None
        assert participants is not None
        assert label is not None
        assert chart is not None
        return toga.Box(
            children=[plot_settings, participants, label, chart],
            style=Pack(direction=COLUMN),
        )

    def _create_plot_settings_layout(self):
        # Create selections
        self.file_format = toga.Selection(
            items=ConversationalSpaceMapAppToga.save_file_formats
        )
        self.file_format.style.padding = ConversationalSpaceMapAppToga.default_padding
        self.file_format.style.flex = ConversationalSpaceMapAppToga.default_flex
        self.path_input = toga.Selection(
            items=self._get_file_history(), on_change=self._set_parser
        )
        self.path_input.style.padding = ConversationalSpaceMapAppToga.default_padding
        self.path_input.readonly = True
        self.path_input.style.flex = 10

        # Create buttons
        self.button = self._button_factory("📄", on_press=self.open_handler)
        self.plot = self._button_factory(
            "🖌", on_press=self.plot_handler, enabled=self.has_path
        )
        self.save = self._button_factory(
            "💾", on_press=self.save_handler, enabled=False
        )
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

    def _create_inital_participants_layout(self):
        self.participants_layout = toga.Box(
            children=[
                toga.Label(
                    "",
                    style=Pack(padding=ConversationalSpaceMapAppToga.default_padding),
                )
            ]
        )
        return self.participants_layout

    def _create_info_layout(self):
        self.label = toga.Label("")
        self.label.style.padding = ConversationalSpaceMapAppToga.default_padding
        return self.label

    def _set_info_layout(self):
        assert self.has_parser
        self.label.text = self._get_info_content()
        self.label.refresh()

    def _create_chart(self):
        self.chart = toga_chart.Chart(style=Pack(flex=1), on_draw=self.draw_chart)
        self.chart.style.padding = ConversationalSpaceMapAppToga.default_padding
        self.chart.style.flex = ConversationalSpaceMapAppToga.default_flex
        return self.chart

    def _create_participants_layout(self):
        assert self.has_path
        self.participants_layout.clear()
        for participant in self.parser.participants:
            self.participants_layout.add(self._create_participant_layout(participant))

    def _create_participant_layout(self, participant: str) -> toga.Box:
        # Create participant label
        label = toga.Label(participant)
        label.style.padding = ConversationalSpaceMapAppToga.default_padding
        label.style.flex = ConversationalSpaceMapAppToga.default_flex

        # Create participant role
        role = toga.Selection(
            items=Constants.Participant,
            id=participant + "_role",
            on_change=self.plot_handler,
        )
        role.style.padding = ConversationalSpaceMapAppToga.default_padding
        role.style.flex = ConversationalSpaceMapAppToga.default_flex

        # Create color picker
        color = toga.Selection(
            items=PlotMap.MapBarPlot.COLORS,
            id=participant + "_color",
            on_change=self.plot_handler,
        )
        color.style.padding = ConversationalSpaceMapAppToga.default_padding
        color.style.flex = ConversationalSpaceMapAppToga.default_flex

        return toga.Box(children=[label, role, color])

    def draw_chart(self, chart, figure, *args, **kwargs):
        if self.has_parser:
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

    def _button_factory(
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
            ConversationalSpaceMapAppToga.default_padding
            if padding is None
            else padding
        )
        button.style.flex = (
            ConversationalSpaceMapAppToga.default_flex if padding is None else flex
        )
        return button

    @staticmethod
    def _set_transparent_background(widget):
        if "macOS" in platform.platform():
            widget.style.background_color = "transparent"

    async def _get_path(self):
        file = toga.OpenFileDialog("Open file", file_types=["txt"])
        return await self.main_window.dialog(file)

    def _set_path(self, path: pathlib.Path):
        assert path.is_file()
        try:
            self.path_input.value = path
        except ValueError:
            self.path_input.items.append(path)
            self.path_input.value = path
        self.plot_title = self.path.stem
        self._set_parser()

    def _update_plot(self):
        self.chart.redraw()
        self.save.enabled = True

    async def _get_save_path(self):
        assert self.has_path
        file = toga.SaveFileDialog(
            "Save file",
            suggested_filename=str(pathlib.Path(self.path).stem),
            file_types=ConversationalSpaceMapAppToga.save_file_formats,
        )
        return await self.main_window.dialog(file)

    def _get_widget_value_by_id(self, key: str, default_value=None):
        if key in self.app.widgets.keys():
            return self.app.widgets[key].value
        return default_value


def main():
    return ConversationalSpaceMapAppToga(
        "ConversationalSpaceMapApp", "ch.manuelbieri.conversationalspacemapapp"
    )
