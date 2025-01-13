import abc
import pathlib

import conversationalspacemapapp.Types.Data as Data


class AbstractParser(abc.ABC):
    """
    Converts aTrain transcripts into a dictionary containing the data for a conversational space map.
    """

    def __init__(self, file: pathlib.Path) -> None:
        self._file = file
        self._content = self._read_file()
        self._map: [Data.Utterance] = self._convert_text()

    @property
    def map(self) -> [Data.Utterance]:
        return sorted(self._map)

    @property
    def content(self) -> str:
        return self._content

    @property
    def participants(self) -> list:
        return sorted(list(set([utterance.speaker for utterance in self._map])))

    @abc.abstractmethod
    def number_of_words_by_speaker(self) -> [int, int]:
        raise NotImplementedError

    def _read_file(self) -> str:
        return self._file.read_text()

    def _clean_transcript(self) -> str:
        return self._content

    @abc.abstractmethod
    def _convert_text(self) -> dict[int:dict]:
        raise NotImplementedError

    @property
    def map_list(self) -> list[int]:
        """
        Return lists of words by utterance by speaker (only applies for two speakers), whereas the first speaker is the
        interviewer and the second speaker is the interviewee.
        """
        output = []
        for utterance in self._map:
            if utterance.number % 2 == 1:
                output.append(-utterance.words)
            else:
                output.append(utterance.words)
        return output
