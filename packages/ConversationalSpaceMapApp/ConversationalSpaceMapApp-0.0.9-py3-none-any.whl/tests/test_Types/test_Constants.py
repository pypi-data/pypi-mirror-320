import unittest

import conversationalspacemapapp.Types.Constants as Constants


class TestCustomConstants(unittest.TestCase):
    def test_interviewer_value(self):
        self.assertEqual(Constants.Participant.Interviewer.constant, -1)

    def test_interviewee_value(self):
        self.assertEqual(Constants.Participant.Interviewee.constant, 1)

    def test_undefined_value(self):
        self.assertEqual(Constants.Participant.Undefined.constant, 0)

    def test_interviewer_name(self):
        self.assertEqual(Constants.Participant.Interviewer.name, "Interviewer")
        self.assertEqual(str(Constants.Participant.Interviewer), "Interviewer")

    def test_interviewee_name(self):
        self.assertEqual(Constants.Participant.Interviewee.name, "Interviewee")
        self.assertEqual(str(Constants.Participant.Interviewee), "Interviewee")

    def test_undefined_name(self):
        self.assertEqual(Constants.Participant.Undefined.name, "Undefined")
        self.assertEqual(str(Constants.Participant.Undefined), "Undefined")
