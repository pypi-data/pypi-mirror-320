from enum import Enum


class Participant(Enum):
    Interviewer = -1
    Interviewee = 1
    Undefined = 0

    @property
    def constant(self):
        return self.value

    def __str__(self):
        if self.value == Participant.Interviewee.value:
            return "Interviewee"
        elif self.value == Participant.Interviewer.value:
            return "Interviewer"
        else:
            return "Undefined"
