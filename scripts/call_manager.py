import logging
import asyncio
from io import BytesIO
from loguru import logger
from pydub import AudioSegment
from signalwire.rest import Client
from vocode.turn_based.input_device.microphone_input import MicrophoneInput
from vocode.turn_based.output_device.speaker_output import SpeakerOutput
from vocode.turn_based.transcriber.whisper_cpp_transcriber import WhisperCPPTranscriber
from vocode.turn_based.synthesizer.gtts_synthesizer import GTTSSynthesizer
from vocode.turn_based.transcriber.whisper_cpp_transcriber import transcribe
from vocode.turn_based.turn_based_conversation import TurnBasedConversation

from voice_agent import AIVoiceAgent

new_agent = AIVoiceAgent("../models/20241206-090817-cruel-interval.tar.gz")

class CustomTurnBasedConversation(TurnBasedConversation):
    def transcribe(self, audio_segment: AudioSegment) -> str:
        print('TRANSCRIBER CALLED:')
        print('AUDIO SEGMENT LEGNTH', len(audio_segment))
        if isinstance(self.transcriber, WhisperCPPTranscriber):
            print('entered')
            try:
                transcription, _ = transcribe(
                    self.transcriber.whisper,
                    self.transcriber.params,
                    self.transcriber.ctx,
                    audio_segment,
                )
                print('Transcription:', transcription)
            except Exception as e:
                logger.error(f"Error during transcription: {e}")
                print(f"Error during transcription: {e}")
        else:
            raise TypeError("transcriber is not an instance of WhisperCPPTranscriber")
        
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
        # Custom behavior before starting speech
        logger.info("Custom behavior before starting speech")

        # Start listening
        if isinstance(self.input_device, MicrophoneInput):
            self.input_device.start_listening()
            print("LISTENING")
            logger.info("Started listening for speech")
        else:
            raise TypeError("input_device is not an instance of MicrophoneInput")

        # Custom behavior after starting speech
        logger.info("Custom behavior after starting speech")

    async def end_speech_and_respond(self):
        # Custom behavior before transcription
        logger.info("Custom behavior before transcription")

        # End listening and get the audio segment
        if isinstance(self.input_device, MicrophoneInput):
            await asyncio.sleep(10)  
            audio_segment = self.input_device.end_listening()
            audio_segment.export("debug_audio_segment.wav", format="wav")
            print('ENDED LISTENING')
            print("Audio segment", len(audio_segment))
            logger.info(f"Audio segment duration: {len(audio_segment)} ms")
        else:
            raise TypeError("input_device is not an instance of MicrophoneInput")

        # Transcribe the human input
        human_input = self.transcribe(audio_segment)
        print("HUMAN_INPUT", human_input)
        logger.info(f"Transcription: {human_input}")

        # Custom behavior after transcription
        logger.info("Custom behavior after transcription")

        # Get the agent's response
        agent_response = await new_agent.respond(human_input)
        print("Agent response", agent_response)
        logger.info(f"Agent response: {agent_response}")

        # Custom behavior before synthesizing response
        logger.info("Custom behavior before synthesizing response")

        # Synthesize the agent's response
        synthesized_response = self.synthesize(agent_response)

        # Custom behavior after synthesizing response
        logger.info("Custom behavior after synthesizing response")

        # Send the synthesized response to the output device
        if isinstance(self.output_device, SpeakerOutput):
            self.output_device.send_audio(synthesized_response)
        else:
            raise TypeError("output_device is not an instance of SpeakerOutput")
        
    


    # async def start_conversation(self, max_turns=10):
    #     for turn in range(max_turns):
    #         try:
    #             logger.info(f"Starting conversation turn {turn + 1}")
    #             self.input_device.start_listening()
    #             await asyncio.sleep(10)  
    #             audio_segment = self.input_device.end_listening()
                
    #             logger.info(f"Audio segment duration: {audio_segment.duration_seconds} seconds")

    #             human_input = self.transcriber.transcribe(audio_segment)
    #             print("HUMAN INPUT", human_input)
    #             logger.info(f"Transcription: {human_input}")

    #             if not human_input:
    #                 print("EMPYT HUMAN INPUT")
    #                 logger.warning("Transcription is empty, skipping this turn.")
    #                 continue

    #             agent_response = await self.agent.respond(human_input)
    #             logger.info(f"Agent response: {agent_response}")

    #             synthesized_response = self.synthesizer.synthesize(agent_response)
    #             self.output_device.send_audio(synthesized_response)

    #         except Exception as e:
    #             logger.error(f"Error during conversation turn: {e}")
    #             break

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

    async def handle_call_flow(
        self, 
        customer_phone: str, 
        whisper_lib: str, 
        whisper_model: str, 
        rasa_model_path: str, 
        use_aws: bool = False
    ):
        self.logger.info(f"Starting AI Voice Agent for customer {customer_phone}...")

        try:
            # Place the initial call
            # self.make_call(customer_phone, webhook_url="http://192.168.8.103:5000/webhook")

            # Initialize conversation components
            input_device = MicrophoneInput.from_default_device()
            output_device = SpeakerOutput.from_default_device()
            transcriber = WhisperCPPTranscriber(
                libname=whisper_lib, 
                fname_model=whisper_model
            )
            agent = AIVoiceAgent(
                rasa_model_path=rasa_model_path, 
                initial_message="Hello Marc"
            )
            synthesizer = GTTSSynthesizer()

            # Create conversation instance
            conversation = CustomTurnBasedConversation(
                input_device=input_device,
                transcriber=transcriber,
                agent=agent,
                synthesizer=synthesizer,
                output_device=output_device
            )

            # Main conversation loop
            max_turns = 10  # Prevent infinite loop
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
            
            
