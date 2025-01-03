import os
import re
import logging
import asyncio
import subprocess
from io import BytesIO
from loguru import logger
from pydub import AudioSegment
from signalwire.rest import Client
from vocode.turn_based.input_device.microphone_input import MicrophoneInput
from vocode.turn_based.output_device.speaker_output import SpeakerOutput
from vocode.turn_based.turn_based_conversation import TurnBasedConversation
from vocode.turn_based.synthesizer.gtts_synthesizer import GTTSSynthesizer
from scripts.voice_agent import AIVoiceAgent


# Initialize the AI Voice Agent with the Rasa model path
new_agent = AIVoiceAgent("./models/20241219-002619-daring-director.tar.gz")


class CustomTurnBasedConversation(TurnBasedConversation):
    """
    Handles conversation logic including audio recording, transcription, and playing pre-recorded audio responses.
    """
    
    def clean_transcription(self, transcription: str) -> str:
        """Clean up the transcription output to remove unnecessary tags and artifacts."""
        # Remove texts in the form [some-text]
        pattern = r'\[.*?\]'
        transcription = re.sub(pattern, '', transcription)
        
        # Split the transcription into lines and clean each line
        lines = transcription.split('\n')
        cleaned_lines = [line.split('] ')[-1].strip() for line in lines if '] ' in line and not line.endswith('[BLANK_AUDIO]')]
        
        # Join the cleaned lines and remove extra spaces
        cleaned_transcription = ' '.join(cleaned_lines).strip()
        cleaned_transcription = re.sub(r'\s+', ' ', cleaned_transcription).strip()
        
        return cleaned_transcription

    def transcribe(self, audio_segment: AudioSegment) -> str:
        """Transcribe the given audio segment using whisper.cpp."""
        logger.info('Transcriber called.')
        logger.info(f'Audio segment length: {len(audio_segment)} ms')

        audio_folder = os.path.join(os.getcwd(), 'audio')
        os.makedirs(audio_folder, exist_ok=True)  # Ensure 'audio' folder exists

        # Define file paths for the recorded and converted audio
        audio_path = os.path.join(audio_folder, 'recorded_audio.wav')
        converted_audio_path = os.path.join(audio_folder, 'converted_audio.wav')

        try:
            # Export the recorded audio segment as WAV
            audio_segment.export(audio_path, format="wav")
            logger.info(f"Audio file saved at: {audio_path}")
        except Exception as e:
            logger.error(f"Failed to export audio file: {e}")
            return ""

        try:
            # Convert the audio to 16kHz, mono, pcm_s16le format using ffmpeg
            command = ["ffmpeg", "-y", "-i", audio_path, "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", converted_audio_path]
            subprocess.run(command, check=True)
            logger.info(f"Converted audio file saved at: {converted_audio_path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to convert audio file: {e.stderr}")
            return ""

        try:
            whisper_path = os.path.join(os.getcwd(), 'whisper.cpp/build/bin/main')
            model_path = os.path.join(os.getcwd(), 'whisper.cpp/models/ggml-base.en.bin')
            command = f"{whisper_path} -m {model_path} -f {converted_audio_path}"
            logger.info(f"Running command: {command}")

            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Whisper transcription failed: {result.stderr}")
                return ""
            
            transcription = result.stdout.strip()
            cleaned_transcription = self.clean_transcription(transcription)
            logger.info(f"Transcription: {cleaned_transcription}")
            return cleaned_transcription
        
        except Exception as e:
            logger.error(f"Error during whisper transcription: {e}")
            return ""

    async def start_speech_and_listen(self):
        """Start listening for speech from the customer."""
        logger.info("Starting speech and listening for customer input.")

        if isinstance(self.input_device, MicrophoneInput):
            self.input_device.start_listening()
            logger.info("Started listening for speech.")
        else:
            raise TypeError("input_device is not an instance of MicrophoneInput")

    async def end_speech_and_respond(self):
        """End the speech input, transcribe it, and respond accordingly."""
        logger.info("Ending speech input and processing the response.")
        if isinstance(self.input_device, MicrophoneInput):
            await asyncio.sleep(10)
            audio_segment = self.input_device.end_listening()
            logger.info(f"Audio segment duration: {len(audio_segment)} ms")
        else:
            raise TypeError("input_device is not an instance of MicrophoneInput")

        human_input = self.transcribe(audio_segment)
        if not human_input or human_input.isspace():
            logger.info("No valid input detected, skipping response.")
            return

        agent_response = await new_agent.respond(human_input)
        logger.info(f"Agent response: {agent_response}")

        try:
            # Play the corresponding pre-recorded audio file
            audio_segment = new_agent.get_pre_recorded_audio(agent_response)
            logger.info("Playing pre-recorded response successfully.")
        except Exception as e:
            logger.error(f"Failed to play pre-recorded audio: {e}")
            return

        if isinstance(self.output_device, SpeakerOutput):
            self.output_device.send_audio(audio_segment)
        else:
            raise TypeError("output_device is not an instance of SpeakerOutput")


class AIConversation:
    """
    Manages the end-to-end process of calling the customer, handling the call flow, and controlling the AI conversation.
    """
    def __init__(self, PROJECT_ID: str, API_TOKEN: str, SPACE_URL: str, signalwire_phone_number: str):
        self.logger = logging.getLogger(__name__)
        self.signalwire_client = Client(PROJECT_ID, API_TOKEN, signalwire_space_url=SPACE_URL)
        self.signalwire_phone_number = signalwire_phone_number

    def make_call(self, customer_phone: str, webhook_url: str) -> None:
        """Initiate a call to the customer."""
        self.logger.info(f"Placing a call to {customer_phone}...")
        try:
            call = self.signalwire_client.calls.create(
                from_=self.signalwire_phone_number,
                to=customer_phone,
                url=webhook_url
            )
            self.logger.info(f"Call placed to {customer_phone}. Call SID: {call.sid}")
        except Exception as e:
            self.logger.error(f"Failed to place call to {customer_phone}: {e}")
            raise

    async def handle_call_flow(self, customer_phone: str, rasa_model_path: str):
        """Handle the entire call flow including listening, transcribing, and playing pre-recorded responses."""
        self.logger.info(f"Starting AI Voice Agent for customer {customer_phone}...")

        try:
            input_device = MicrophoneInput.from_default_device()
            output_device = SpeakerOutput.from_default_device()
            agent = AIVoiceAgent(rasa_model_path=rasa_model_path, initial_message="Hello Jhon!")
            synthesizer = GTTSSynthesizer()
            
            conversation = CustomTurnBasedConversation(
                input_device=input_device,
                agent=agent,
                output_device=output_device,
                transcriber=None,
                synthesizer=synthesizer
            )

            max_turns = 40  
            for _ in range(max_turns):
                try:
                    await conversation.start_speech_and_listen()
                    await conversation.end_speech_and_respond()
                except Exception as turn_error:
                    self.logger.error(f"Error in conversation turn: {turn_error}")
                    break

        except KeyboardInterrupt:
            self.logger.info("Gracefully shutting down AI Voice Agent.")
        except Exception as e:
            self.logger.error(f"Unexpected error in conversation: {e}")
