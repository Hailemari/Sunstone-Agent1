import asyncio
import logging
from scripts.call_manager import AIConversation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():

    # Configuration parameters
    config = {
        'SIGNALWIRE_PROJECT_ID': "92cbac4c-dc02-47bf-8c77-16b3f30952e2",
        'SIGNALWIRE_API_TOKEN': "PT2aa83650dec5789e3686334f7436c93c5165ecb5a6b6dfa2",
        'SIGNALWIRE_SPACE_URL': "sunstone.signalwire.com",
        'SIGNALWIRE_PHONE_NUMBER': "+18336529066",
        'CUSTOMER_PHONE': "+18777797248",
        'RASA_MODEL_PATH': "./models/20241219-002619-daring-director.tar.gz",
        'WEBHOOK_URL': "https://ee13-198-44-138-112.ngrok-free.app/webhook"
    }

    try:
        # Initialize AI Conversation
        ai_conversation = AIConversation(
            PROJECT_ID=config['SIGNALWIRE_PROJECT_ID'],
            API_TOKEN=config['SIGNALWIRE_API_TOKEN'],
            SPACE_URL=config['SIGNALWIRE_SPACE_URL'],
            signalwire_phone_number=config['SIGNALWIRE_PHONE_NUMBER']
        )
        
        # Make the call and get the call SID
        call_sid = ai_conversation.make_call(
            customer_phone=config['CUSTOMER_PHONE'],
            webhook_url=config['WEBHOOK_URL']
        )

        # Wait for the call to be answered (I need to implement a mechanism to detect this)
        # For simplicity, I'll just wait for a few seconds
        await asyncio.sleep(10)
        # Run the async conversation
        await ai_conversation.handle_call_flow(
            customer_phone=config['CUSTOMER_PHONE'],
            rasa_model_path=config['RASA_MODEL_PATH']
        )

    except Exception as e:
        logger.error(f"Unexpected error in main execution: {e}")

if __name__ == "__main__":
    asyncio.run(main())
