import requests
import os
from dotenv import load_dotenv
from gtts import gTTS
from pydub import AudioSegment

# Load environment variables from .env file
load_dotenv()

PIPEDRIVE_API_URL = "https://api.pipedrive.com/v1"
PIPEDRIVE_API_TOKEN = "1b58641cb2242bc9a2df2d1fa7abba19bbb29b6b"

def fetch_all_leads():
    """
    Fetch all leads data from Pipedrive.

    :return: A list of dictionaries containing the leads data.
    """
    url = f"{PIPEDRIVE_API_URL}/leads"
    params = {
        "api_token": PIPEDRIVE_API_TOKEN
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch leads data: {response.status_code}")
        return None

def fetch_lead_data(lead_id):
    """
    Fetch lead data from Pipedrive using the lead ID.

    :param lead_id: The ID of the lead to fetch data for.
    :return: A dictionary containing the lead data.
    """
    url = f"{PIPEDRIVE_API_URL}/deals/{lead_id}"
    params = {
        "api_token": PIPEDRIVE_API_TOKEN
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch lead data: {response.status_code}")
        return None

def generate_dynamic_text(lead_data):
    """
    Generate dynamic text for pre-recorded audio files using lead data.

    :param lead_data: A dictionary containing the lead data.
    :return: A string with the generated text.
    """
    lead_name = lead_data.get('data', {}).get('person_name', 'there')
    lead_company = lead_data.get('data', {}).get('org_name', 'your company')
    lead_project = lead_data.get('data', {}).get('title', 'your project')

    text = f"Hi {lead_name}, this is Olivia from Sunstone Digital. I see that you recently purchased {lead_project} for {lead_company}. Is there a project behind this?"
    return text

def generate_audio_from_text(text, filename):
    """
    Generate an audio file from the given text.

    :param text: The text to convert to audio.
    :param filename: The name of the audio file to save.
    """
    tts = gTTS(text=text, lang='en')
    tts.save(filename)
    print(f"Audio file saved as {filename}")

def combine_audio_segments(segments, output_filename):
    """
    Combine multiple audio segments into a single audio file.

    :param segments: A list of audio segment filenames.
    :param output_filename: The name of the output audio file.
    """
    combined = AudioSegment.empty()
    for segment in segments:
        audio = AudioSegment.from_file(segment)
        combined += audio
    combined.export(output_filename, format="mp3")
    print(f"Combined audio file saved as {output_filename}")
    
if __name__ == "__main__":
    lead_id = "1"  # Replace with an actual lead ID
    lead_data = fetch_lead_data(lead_id)
    if lead_data:
        dynamic_text = generate_dynamic_text(lead_data)
        print(dynamic_text)
        dynamic_audio_filename = "dynamic_audio.mp3"
        generate_audio_from_text(dynamic_text, dynamic_audio_filename)

        # List of pre-recorded audio segments and the dynamic audio segment
        audio_segments = [
            "pre_recorded_intro.mp3",  # Pre-recorded intro segment
            dynamic_audio_filename,    # Dynamic audio segment
            "pre_recorded_outro.mp3"   # Pre-recorded outro segment
        ]

        # Combine the audio segments into a single audio file
        combine_audio_segments(audio_segments, "final_audio.mp3")