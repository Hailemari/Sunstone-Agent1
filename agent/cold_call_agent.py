import os
from gtts import gTTS
import whisper
from signalwire.rest import Client as SignalWireClient
from vocode import Vocode
from rasa.core.agent import Agent
from rasa.core.interpreter import RasaNLUInterpreter
from dotenv import load_dotenv
import asyncio

from response_handler import handle_responses

# SignalWire credentials
load_dotenv()

SIGNALWIRE_PROJECT_ID = os.getenv("SIGNALWIRE_PROJECT_ID")
SIGNALWIRE_API_TOKEN = os.getenv("SIGNALWIRE_API_TOKEN")
SIGNALWIRE_SPACE = os.getenv("SIGNALWIRE_SPACE")
SIGNALWIRE_PHONE_NUMBER = os.getenv("SIGNALWIRE_PHONE_NUMBER")

# Initialize SignalWire client
signalwire_client = SignalWireClient(SIGNALWIRE_PROJECT_ID, SIGNALWIRE_API_TOKEN, SIGNALWIRE_SPACE)

# Initialize Vocode client
vocode_client = Vocode(api_key="vocode_api_key")

# Initialize Rasa agent
interpreter = RasaNLUInterpreter("models/nlu")
agent = Agent.load("models/dialogue", interpreter=interpreter)

def play_audio_from_s3(file_name):
    """Play an audio file from S3 using Vocode."""
    s3_url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/audio/{file_name}"
    vocode_client.play_audio(s3_url)

def synthesize_speech(text, output_file):
    """Synthesize speech using gTTS."""
    tts = gTTS(text=text, lang="en")
    tts.save(output_file)
    print(f"Saved synthesized speech to {output_file}")

def transcribe_audio(audio_file):
    """Transcribe audio using OpenAI Whisper."""
    model = whisper.load_model("base")
    result = model.transcribe(audio_file)
    return result['text']

def initiate_call(to_phone_number):
    """Initiate a call using SignalWire."""
    call = signalwire_client.calls.create(
        from_=SIGNALWIRE_PHONE_NUMBER,
        to=to_phone_number,
        url="http://server-url/voice-response.xml"  # Replace with server URL for handling calls
    )
    print(f"Initiated call to {to_phone_number}, Call SID: {call.sid}")

def handle_voice_request():
    """Handle the initial voice request using Vocode."""
    response = vocode_client.create_voice_response()
    response.play_audio("greeting.mp3")
    response.record_audio("response.mp3")
    return response

async def handle_conversation():
    """Handle the conversation using Rasa and gTTS."""
    print("Conversation started. Listening for user responses...")

    while True:
        # Simulate receiving user input via audio
        user_input = transcribe_audio("response.mp3").lower()
        print(f"User said: {user_input}")

        if user_input:
            # Get Rasa's response
            responses = await agent.handle_text(user_input)

            # Process responses and play corresponding audio
            handle_responses(responses, play_audio_from_s3)


def main():
    """Main function to run the cold call agent."""
    lead_phone_number = input("Enter the lead's phone number: ")

    # Step 1: Initiate Call
    initiate_call(lead_phone_number)

    # Step 2: Handle the conversation
    asyncio.run(handle_conversation())

if __name__ == "__main__":
    main()