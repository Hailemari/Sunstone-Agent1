import logging
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from pydub.exceptions import CouldntDecodeError
from pydub import AudioSegment
from rasa.core.agent import Agent

class AIVoiceAgent:
    def __init__(self, rasa_model_path: str, aws_bucket: str = None, initial_message: str = None):
        self.logger = logging.getLogger(__name__)
        self.aws_bucket = aws_bucket
        self.s3_client = boto3.client('s3') if aws_bucket else None
        self.initial_message = initial_message
        self.agent = self.load_rasa_model(rasa_model_path)

    def load_rasa_model(self, model_path: str) -> Agent:
        self.logger.info(f"Loading Rasa model from {model_path}...")
        try:
            agent = Agent.load(model_path)
            self.logger.info("Rasa model loaded successfully.")
            return agent
        except Exception as e:
            self.logger.error(f"Failed to load Rasa model from {model_path}: {e}")
            raise

    async def respond(self, human_input: str) -> str:
        print("HUMAN_INPUT", type(human_input))
        self.logger.info(f"Processing input: {human_input}")
        try:
            responses = await self.agent.handle_text(human_input)
            print("responses", responses)
            if responses:
                response_text = responses[0]['text']
                self.logger.info(f"Rasa response: {response_text}")
                return response_text
            
            self.logger.warning("No response from Rasa model.")
            return "I didn't understand that. Could you please repeat?"
        
        except Exception as e:
            self.logger.error(f"Error processing Rasa input: {e}")
            return "Sorry, I'm experiencing some technical difficulties."

    def get_pre_recorded_audio(self, response_text: str) -> AudioSegment:
        # Mapping responses to audio files
        audio_file_map = {
            "positive response": "positive_response.mp3",
            "negative response": "negative_response.mp3",
            # Add more mappings as needed
        }
        
        filename = audio_file_map.get(response_text.lower(), "default_response.mp3")
        local_path = f'/tmp/{filename}'
        
        try:
            # Download from S3 if AWS is configured
            if self.s3_client:
                self.logger.info(f"Downloading {filename} from S3 bucket {self.aws_bucket}...")
                self.s3_client.download_file(self.aws_bucket, f'audio/{filename}', local_path)
            else:
                local_path = f'./audio/{filename}'
            
            self.logger.info(f"Loading audio file from {local_path}...")
            audio = AudioSegment.from_file(local_path)
            return audio
        
        except (BotoCoreError, ClientError, CouldntDecodeError, FileNotFoundError) as e:
            self.logger.error(f"Failed to process audio file {filename}: {e}")
            raise