import matplotlib.pyplot as plt
import toga
import conversationalspacemapapp.Parser.TimestampParser as TranscriptParser


class MapBarPlot:
    COLORS: list[str] = ["salmon", "gold", "lawngreen", "turquoise", "thistle"]

    def __init__(
        self,
        parser: TranscriptParser.AbstractParser,
        fig: plt.figure,
        ax: plt.Axes,
        app: toga.App,
    ):
        self.participants = parser.participants
        self.map = parser.map
        self.ax = ax
        self.fig = fig
        self.app = app

    def plot(self, title: str):
        xlim_num = 0
        for utterance in self.map:
            self.ax.barh(
                utterance.number,
                utterance.words
                * self.app._get_participant_role(utterance.speaker).constant,
                align="center",
                height=0.8,
                color=self.app._get_participant_color(utterance.speaker),
            )
            xlim_num = max([abs(utterance.words) for utterance in self.map]) * 1.1
        index = [*range(1, len(self.map) + 1)]

        # Set x-axis
        self.ax.set_xlim([-xlim_num, xlim_num])
        self.ax.xaxis.grid(
            True, linestyle="--", which="major", color="grey", alpha=0.25
        )

        # Set y-axis
        self.ax.set_ylim([-2, max(index) + 2])
        self.ax.set_yticks(index)

        # Set plot labels
        self.ax.set_title("Conversational Map Space " + title)
        self.ax.text(
            xlim_num / 2,
            -1,
            "Participant's words per utterance",
            horizontalalignment="center",
        )
        self.ax.text(
            -xlim_num / 2,
            -1,
            "Interviewer's words per utterance",
            horizontalalignment="center",
        )
        self.ax.set_ylabel("Utterance (bottom = start of interview)")
        self.fig.tight_layout()

    def save(self, filename: str):
        self.fig.savefig(filename, dpi=300)
