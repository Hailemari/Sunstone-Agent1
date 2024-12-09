import asyncio
import logging
from dotenv import load_dotenv

from voice_agent import AIVoiceAgent
from call_manager import AIConversation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    # Load environment variables
    load_dotenv()

    # Configuration parameters
    config = {
        'SIGNALWIRE_PROJECT_ID': "92cbac4c-dc02-47bf-8c77-16b3f30952e2",
        'SIGNALWIRE_API_TOKEN': "PT2aa83650dec5789e3686334f7436c93c5165ecb5a6b6dfa2",
        'SIGNALWIRE_SPACE_URL': "sunstone.signalwire.com",
        'SIGNALWIRE_PHONE_NUMBER': "+18336529066",
        'CUSTOMER_PHONE': "+18777797248",
        'WHISPER_LIB': "/home/hailemariam/Sunstone/ai_cold_call_agent/libwhisper.so",
        'WHISPER_MODEL': "/home/hailemariam/Sunstone/ai_cold_call_agent/whisper.tiny.bin",
        'RASA_MODEL_PATH': "/home/hailemariam/Sunstone/ai_cold_call_agent/models/20241206-090817-cruel-interval.tar.gz",
        'USE_AWS': False
    }

    # Validate required configurations
    required_keys = [
        'SIGNALWIRE_PROJECT_ID', 'SIGNALWIRE_API_TOKEN', 
        'SIGNALWIRE_SPACE_URL', 'SIGNALWIRE_PHONE_NUMBER', 
        'CUSTOMER_PHONE'
    ]
    for key in required_keys:
        if not config[key]:
            logger.error(f"Missing required configuration: {key}")
            return

    try:
        # Initialize AI Conversation
        ai_conversation = AIConversation(
            PROJECT_ID=config['SIGNALWIRE_PROJECT_ID'],
            API_TOKEN=config['SIGNALWIRE_API_TOKEN'],
            SPACE_URL=config['SIGNALWIRE_SPACE_URL'],
            signalwire_phone_number=config['SIGNALWIRE_PHONE_NUMBER']
        )

        # Run the async conversation
        asyncio.run(
            ai_conversation.handle_call_flow(
                customer_phone=config['CUSTOMER_PHONE'],
                whisper_lib=config['WHISPER_LIB'],
                whisper_model=config['WHISPER_MODEL'],
                rasa_model_path=config['RASA_MODEL_PATH'],
                use_aws=config['USE_AWS']
            )
        )

    except Exception as e:
        logger.error(f"Unexpected error in main execution: {e}")

if __name__ == "__main__":
    main()