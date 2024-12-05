import unittest
from unittest.mock import patch, MagicMock
from agent.cold_call_agent import initiate_call, handle_conversation, transcribe_audio, synthesize_speech
import asyncio

class TestColdCallAgent(unittest.TestCase):

    @patch('agent.cold_call_agent.SignalWireClient')
    def test_initiate_call(self, MockSignalWireClient):
        mock_client = MockSignalWireClient.return_value
        mock_client.calls.create.return_value.sid = '12345'
        
        initiate_call('1234567890')
        
        mock_client.calls.create.assert_called_once_with(
            from_='SIGNALWIRE_PHONE_NUMBER',
            to='1234567890',
            url='http://server-url/voice-response.xml'
        )
        print("Initiate call test passed.")

    @patch('agent.cold_call_agent.whisper.load_model')
    def test_transcribe_audio(self, MockWhisperModel):
        mock_model = MockWhisperModel.return_value
        mock_model.transcribe.return_value = {'text': 'Hello, this is a test.'}
        
        result = transcribe_audio('test_audio.mp3')
        
        self.assertEqual(result, 'Hello, this is a test.')
        print("Transcribe audio test passed.")

    @patch('agent.cold_call_agent.gTTS')
    def test_synthesize_speech(self, MockGTTS):
        mock_tts = MockGTTS.return_value
        mock_tts.save = MagicMock()
        
        synthesize_speech('Hello, this is a test.', 'output.mp3')
        
        mock_tts.save.assert_called_once_with('output.mp3')
        print("Synthesize speech test passed.")

    @patch('agent.cold_call_agent.play_audio_from_s3')
    @patch('agent.cold_call_agent.transcribe_audio')
    @patch('agent.cold_call_agent.agent.handle_text')
    def test_handle_conversation(self, MockHandleText, MockTranscribeAudio, MockPlayAudioFromS3):
        MockTranscribeAudio.return_value = 'greeting'
        MockHandleText.return_value = [{'text': 'greeting'}]
        
        async def run_handle_conversation():
            await handle_conversation()
        
        asyncio.run(run_handle_conversation())
        
        MockPlayAudioFromS3.assert_called_with('greeting.mp3')
        print("Handle conversation test passed.")

if __name__ == '__main__':
    unittest.main()