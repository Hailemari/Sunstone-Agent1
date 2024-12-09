import logging
from signalwire.rest import Client
from vocode.turn_based.input_device.microphone_input import MicrophoneInput
from vocode.turn_based.output_device.speaker_output import SpeakerOutput
from vocode.turn_based.transcriber.whisper_cpp_transcriber import WhisperCPPTranscriber
from vocode.turn_based.synthesizer.gtts_synthesizer import GTTSSynthesizer
from vocode.turn_based.turn_based_conversation import TurnBasedConversation

from voice_agent import AIVoiceAgent

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
            self.make_call(customer_phone, webhook_url="http://192.168.8.103:5000/webhook")

            # Initialize conversation components
            input_device = MicrophoneInput.from_default_device()
            output_device = SpeakerOutput.from_default_device()
            transcriber = WhisperCPPTranscriber(
                libname=whisper_lib, 
                fname_model=whisper_model
            )
            agent = AIVoiceAgent(
                rasa_model_path=rasa_model_path, 
                aws_bucket='s3-bucket-name' if use_aws else None,
                initial_message="Hello, how can I help you today?"
            )
            synthesizer = GTTSSynthesizer()

            # Create conversation instance
            conversation = TurnBasedConversation(
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
                    conversation.start_speech()
                    conversation.end_speech_and_respond()
                    turn_count += 1
                except Exception as turn_error:
                    self.logger.error(f"Error in conversation turn: {turn_error}")
                    break

        except KeyboardInterrupt:
            self.logger.info("Gracefully shutting down AI Voice Agent.")
        except Exception as e:
            self.logger.error(f"Unexpected error in conversation: {e}")