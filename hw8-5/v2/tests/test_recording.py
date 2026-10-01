import unittest

from v2.activities.recording import RecordingSession
from v2.community.channels import VoiceMessage


class RecordingSessionTest(unittest.TestCase):
    def test_generate_replay_formats_recorded_voices(self) -> None:
        session = RecordingSession("3")
        session.addVoice(VoiceMessage("4", "line one"))
        session.addVoice(VoiceMessage("4", "line two"))
        self.assertEqual(session.generateReplay(), "[Record Replay] line one\nline two")


if __name__ == "__main__":
    unittest.main()
