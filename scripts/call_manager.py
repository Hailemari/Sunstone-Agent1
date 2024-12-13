import os
import logging
import asyncio
import subprocess
from io import BytesIO
from loguru import logger
from pydub import AudioSegment
from signalwire.rest import Client
from vocode.turn_based.input_device.microphone_input import MicrophoneInput
from vocode.turn_based.output_device.speaker_output import SpeakerOutput
from vocode.turn_based.synthesizer.gtts_synthesizer import GTTSSynthesizer
from vocode.turn_based.turn_based_conversation import TurnBasedConversation

from voice_agent import AIVoiceAgent

new_agent = AIVoiceAgent("/home/hailemariam/Sunstone/ai_cold_call_agent/models/20241206-090817-cruel-interval.tar.gz")

class CustomTurnBasedConversation(TurnBasedConversation):
    def clean_transcription(self, transcription: str) -> str:
        # Remove timestamps, [BLANK_AUDIO], and any non-verbal tags
        lines = transcription.split('\n')
        cleaned_lines = [line.split('] ')[-1].strip() for line in lines if '] ' in line and not line.endswith('[BLANK_AUDIO]')]
        cleaned_transcription = ' '.join(cleaned_lines).strip()
        return cleaned_transcription

    def transcribe(self, audio_segment: AudioSegment) -> str:
        print('TRANSCRIBER CALLED:')
        print('AUDIO SEGMENT LENGTH:', len(audio_segment))

        # Define path to export audio to the 'audio' folder
        audio_folder = os.path.join(os.getcwd(), 'audio')
        os.makedirs(audio_folder, exist_ok=True)  # Ensure 'audio' folder exists
        audio_path = os.path.join(audio_folder, 'recorded_audio.wav')
        converted_audio_path = os.path.join(audio_folder, 'converted_audio.wav')

        # Export the audio segment as a WAV file
        try:
            audio_segment.export(audio_path, format="wav")
            print(f"Audio file saved at: {audio_path}")
        except Exception as e:
            logger.error(f"Failed to export audio file: {e}")
            return ""

        # Convert the audio file to the required format using ffmpeg
        try:
            command = [
                "ffmpeg", "-i", audio_path, "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", converted_audio_path
            ]
            subprocess.run(command, check=True)
            print(f"Converted audio file saved at: {converted_audio_path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to convert audio file: {e.stderr}")
            return ""

        # Use whisper.cpp command to transcribe the audio
        try:
            whisper_path = os.path.join(os.getcwd(), 'whisper.cpp/build/bin/main')
            model_path = os.path.join(os.getcwd(), 'whisper.cpp/models/ggml-base.en.bin')
            command = f"{whisper_path} -m {model_path} -f {converted_audio_path}"
            print(f"Running command: {command}")
            
            # Run the whisper.cpp command to transcribe the audio
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Whisper transcription failed: {result.stderr}")
                print(f"Whisper transcription failed: {result.stderr}")
                return ""
            
            print('RESULT ---------------------------------- ', result)
            transcription = result.stdout.strip()
            print('Transcription:', transcription)
            cleaned_transcription = self.clean_transcription(transcription)
            print('Cleaned Transcription:', cleaned_transcription)
            return cleaned_transcription
        
        except Exception as e:
            logger.error(f"Error during whisper transcription: {e}")
            print(f"Error during whisper transcription: {e}")
            return ""
    
    def synthesize(self, text) -> AudioSegment:
        if isinstance(self.synthesizer, GTTSSynthesizer):
            tts = self.synthesizer.gTTS(text)
            audio_file = BytesIO()
            tts.write_to_fp(audio_file)
            audio_file.seek(0)
            return AudioSegment.from_mp3(audio_file)  # type: ignore
        else:
            raise TypeError("synthesizer is not an instance of GTTSSynthesizer")

    async def start_speech_and_listen(self):
        logger.info("Custom behavior before starting speech")

        if isinstance(self.input_device, MicrophoneInput):
            self.input_device.start_listening()
            print("LISTENING")
            logger.info("Started listening for speech")
        else:
            raise TypeError("input_device is not an instance of MicrophoneInput")

    async def end_speech_and_respond(self):
        logger.info("Custom behavior before transcription")
        if isinstance(self.input_device, MicrophoneInput):
            await asyncio.sleep(10)  
            audio_segment = self.input_device.end_listening()
            audio_segment.export("debug_audio_segment.wav", format="wav")
            print('ENDED LISTENING')
            print("Audio segment", len(audio_segment))
            logger.info(f"Audio segment duration: {len(audio_segment)} ms")
        else:
            raise TypeError("input_device is not an instance of MicrophoneInput")

        human_input = self.transcribe(audio_segment)
        print("HUMAN_INPUT", human_input)
        logger.info(f"Transcription: {human_input}")

        if not human_input or human_input.isspace():
            logger.info("No valid input detected, skipping response.")
            return

        logger.info("Custom behavior after transcription")

        agent_response = await new_agent.respond(human_input)
        if human_input.strip() == agent_response.strip():
            logger.error("Agent response is identical to user input, skipping output.")
            return

        print("Agent response", agent_response)
        logger.info(f"Agent response: {agent_response}")

        logger.info("Custom behavior before synthesizing response")
        synthesized_response = self.synthesize(agent_response)
        logger.info("Custom behavior after synthesizing response")

        if isinstance(self.output_device, SpeakerOutput):
            self.output_device.send_audio(synthesized_response)
        else:
            raise TypeError("output_device is not an instance of SpeakerOutput")


class AIConversation:
    def __init__(self, PROJECT_ID: str, API_TOKEN: str, SPACE_URL: str, signalwire_phone_number: str):
        self.logger = logging.getLogger(__name__)
        self.signalwire_client = Client(PROJECT_ID, API_TOKEN, signalwire_space_url=SPACE_URL)
        self.signalwire_phone_number = signalwire_phone_number

    def make_call(self, customer_phone: str, webhook_url: str) -> None:
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

    async def handle_call_flow(self, customer_phone: str, whisper_lib: str, whisper_model: str, rasa_model_path: str, use_aws: bool = False):
        self.logger.info(f"Starting AI Voice Agent for customer {customer_phone}...")

        try:
            input_device = MicrophoneInput.from_default_device()
            output_device = SpeakerOutput.from_default_device()
            agent = AIVoiceAgent(rasa_model_path=rasa_model_path, initial_message="Hello Marc")
            synthesizer = GTTSSynthesizer()

            conversation = CustomTurnBasedConversation(
                input_device=input_device,
                transcriber=None,  # Not used anymore
                agent=agent,
                synthesizer=synthesizer,
                output_device=output_device
            )

            max_turns = 10  
            turn_count = 0

            while turn_count < max_turns:
                try:
                    await conversation.start_speech_and_listen()
                    print('NO ERROR 1')
                    await conversation.end_speech_and_respond()
                    print('NO ERROR')
                    turn_count += 1
                except Exception as turn_error:
                    self.logger.error(f"Error in conversation turn: {turn_error}")
                    break

        except KeyboardInterrupt:
            self.logger.info("Gracefully shutting down AI Voice Agent.")
        except Exception as e:
            self.logger.error(f"Unexpected error in conversation: {e}")
            