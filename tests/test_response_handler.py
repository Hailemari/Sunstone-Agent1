import unittest
from unittest.mock import Mock
from agent.response_handler import handle_responses

class TestHandleResponses(unittest.TestCase):
    def setUp(self):
        """Set up mock for play_audio_from_s3."""
        self.mock_play_audio = Mock()

    def test_greeting_response(self):
        """Test that greeting.mp3 is played for a greeting response."""
        responses = [{"text": "Hi there!"}]
        handle_responses(responses, self.mock_play_audio)
        self.mock_play_audio.assert_called_once_with("greeting.mp3")

    def test_positive_response(self):
        """Test that positive_response.mp3 is played for a positive response."""
        responses = [{"text": "You recently purchased a new domain."}]
        handle_responses(responses, self.mock_play_audio)
        self.mock_play_audio.assert_called_once_with("positive_response.mp3")

    def test_negative_response(self):
        """Test that negative_response.mp3 is played for a negative response."""
        responses = [{"text": "I’m sorry to hear that."}]
        handle_responses(responses, self.mock_play_audio)
        self.mock_play_audio.assert_called_once_with("negative_response.mp3")

    def test_case_insensitivity(self):
        """Test that the function is case-insensitive."""
        responses = [{"text": "HI THERE!"}]
        handle_responses(responses, self.mock_play_audio)
        self.mock_play_audio.assert_called_once_with("greeting.mp3")

    def test_unknown_response(self):
        """Test that small_talk_general.mp3 is played for an unknown response."""
        responses = [{"text": "This is a random response."}]
        handle_responses(responses, self.mock_play_audio)
        self.mock_play_audio.assert_called_once_with("small_talk_general.mp3")

    def test_multiple_responses(self):
        """Test that multiple responses are handled correctly."""
        responses = [
            {"text": "Hi there!"},
            {"text": "You recently purchased a domain."},
            {"text": "I’m sorry to hear that."}
        ]
        handle_responses(responses, self.mock_play_audio)
        expected_calls = [
            unittest.mock.call("greeting.mp3"),
            unittest.mock.call("positive_response.mp3"),
            unittest.mock.call("negative_response.mp3"),
        ]
        self.mock_play_audio.assert_has_calls(expected_calls, any_order=False)

    def test_empty_responses(self):
        """Test that no audio is played if the responses list is empty."""
        responses = []
        handle_responses(responses, self.mock_play_audio)
        self.mock_play_audio.assert_not_called()

if __name__ == "__main__":
    unittest.main()
