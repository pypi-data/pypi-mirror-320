from dataclasses import dataclass


@dataclass
class Utterance:
    number: int
    speaker: str
    words: int

    def __lt__(self, other):
        return self.number < other.number
