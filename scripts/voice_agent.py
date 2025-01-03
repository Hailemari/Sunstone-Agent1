import logging
import os
from pydub.exceptions import CouldntDecodeError
from pydub import AudioSegment
from rasa.core.agent import Agent
from scripts.mapping import audio_file_map


class AIVoiceAgent:
    """
    A class that represents an AI Voice Agent that interacts with a Rasa model to generate responses 
    and retrieve pre-recorded audio files based on the agent's response.
    """
    def __init__(self, rasa_model_path: str, initial_message: str = None):
        """
        Initialize the AIVoiceAgent.
        
        :param rasa_model_path: Path to the Rasa model.
        :param initial_message: Optional initial message to greet the user.
        """
        self.logger = logging.getLogger(__name__)
        self.initial_message = initial_message
        self.agent = self.load_rasa_model(rasa_model_path)

    def load_rasa_model(self, model_path: str) -> Agent:
        """
        Load the Rasa model from the specified path.

        :param model_path: Path to the Rasa model file.
        :return: An instance of the loaded Rasa Agent.
        """
        self.logger.info(f"Loading Rasa model from {model_path}...")
        try:
            agent = Agent.load(model_path)
            self.logger.info("Rasa model loaded successfully.")
            return agent
        except Exception as e:
            self.logger.error(f"Failed to load Rasa model: {e}")
            raise

    async def respond(self, human_input: str) -> str:
        """
        Get a response from the Rasa agent for the given human input.

        :param human_input: The user's spoken or transcribed input.
        :return: The response from the Rasa model as a string.
        """
        self.logger.info(f"Processing input: {human_input}")
        try:
            responses = await self.agent.handle_text(human_input)
            print("---------------------------------------", responses)
            if responses:
                response_text = responses[0].get('custom', '')
                if response_text:
                    rasa_response = response_text.get('audio', '')
                    self.logger.info(f"Rasa response: {rasa_response}")
                return rasa_response
            self.logger.warning("No response from Rasa model.")
            return "I didn't understand that. Could you please repeat?"
        except Exception as e:
            self.logger.error(f"Error processing Rasa input: {e}")
            return "Sorry, I'm experiencing some technical difficulties."

    def get_pre_recorded_audio(self, response_text: str) -> AudioSegment:
        """
        Get the pre-recorded audio file that corresponds to the response text.

        :param response_text: The text of the response to use as a lookup key for the audio file.
        :return: An AudioSegment object representing the audio file.
        """
        response_key = response_text.lower() # Format the key to match the mapping
        filename = audio_file_map.get(response_key)
        
        if not filename:
            self.logger.warning(f"No audio mapping found for '{response_text}'. Using default audio file.")
            filename = "3. I didn’t catch that..wav"
        
        audio_path = os.path.join(os.getcwd(), 'Agent_1_audio', filename)
        
        try:
            if not os.path.isfile(audio_path):
                raise FileNotFoundError(f"Audio file not found at: {audio_path}")
            
            self.logger.info(f"Loading audio file from {audio_path}...")
            audio = AudioSegment.from_file(audio_path)
            return audio
        
        except FileNotFoundError as e:
            self.logger.error(f"Audio file not found: {e}")
            raise
        except CouldntDecodeError as e:
            self.logger.error(f"Failed to decode audio file '{filename}': {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error occurred while loading audio file '{filename}': {e}")
            raise
