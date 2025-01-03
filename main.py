import os
import json
import logging
import speech_recognition as sr
from pydub import AudioSegment
from pydub.playback import play
from fuzzywuzzy import fuzz
from signalwire.rest import Client as SignalWireClient
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# SignalWire credentials
SIGNALWIRE_PROJECT_ID = 'your_project_id'
SIGNALWIRE_API_TOKEN = 'your_api_token'
SIGNALWIRE_SPACE_URL = 'your_space_url'
SIGNALWIRE_PHONE_NUMBER = 'your_signalwire_phone_number'
LEAD_PHONE_NUMBER = 'lead_phone_number'

# Path to the audio folder
AUDIO_FOLDER = "Agent_1_audio"

# Load transcriptions from JSON file
with open('transcriptions.json', 'r') as f:
    transcriptions = json.load(f)

# Define potential lead responses
potential_responses = {
    "Agent #1 (1).wav": ["I'm good, thanks. How are you?", "I'm fine, thank you. How about you?", "Doing well, thanks for asking."],
    "Agent #1 (3).wav": ["It's for the e-commerce industry.", "I'm in the healthcare industry.", "It's for a tech startup."],
    "Agent #1 (2).wav": ["Yes, I'm planning to launch a new website.", "No, I just bought it for future use.", "I'm still figuring out what to do with it."],
    "Q1 rebuttals 1, 2, 4, 6, 7 (row 19).wav": ["Yes, I'm planning to launch a new website.", "No, I just bought it for future use.", "I'm still figuring out what to do with it."],
    "Q1 rebuttals 3 (row 21).wav": ["Yes, I'm planning to launch a new website.", "No, I just bought it for future use.", "I'm still figuring out what to do with it."],
    "Q1 rebuttals 9&10 (row 27).wav": ["Yes, I'm planning to launch a new website.", "No, I just bought it for future use.", "I'm still figuring out what to do with it."],
    "Q1 rebuttals 5 (row 23).wav": ["Yes, I'm planning to launch a new website.", "No, I just bought it for future use.", "I'm still figuring out what to do with it."],
    "Q1 rebuttals 11 (row 29).wav": ["Yes, I'm planning to launch a new website.", "No, I just bought it for future use.", "I'm still figuring out what to do with it."],
    "Q 3&4 rebuttals 3.wav": ["It's for the e-commerce industry.", "I'm in the healthcare industry.", "It's for a tech startup."],
    "Agent #1 (4 education).wav": ["Sure, I can check it out.", "I'm a bit busy right now.", "Maybe later, I'm in the middle of something."],
    "Agent #1 (4 ecommerce).wav": ["Sure, I can check it out.", "I'm a bit busy right now.", "Maybe later, I'm in the middle of something."],
    "Agent #1 (4 yoga).wav": ["Sure, I can check it out.", "I'm a bit busy right now.", "Maybe later, I'm in the middle of something."],
    "Agent #1 (4 insurance).wav": ["Sure, I can check it out.", "I'm a bit busy right now.", "Maybe later, I'm in the middle of something."],
    "Agent #1 (4 automotive).wav": ["Sure, I can check it out.", "I'm a bit busy right now.", "Maybe later, I'm in the middle of something."],
    "Agent #1 (4 food).wav": ["Sure, I can check it out.", "I'm a bit busy right now.", "Maybe later, I'm in the middle of something."],
    "Agent #1 (4 fashion).wav": ["Sure, I can check it out.", "I'm a bit busy right now.", "Maybe later, I'm in the middle of something."],
    "Agent #1 (4 medical).wav": ["Sure, I can check it out.", "I'm a bit busy right now.", "Maybe later, I'm in the middle of something."],
    "Agent #1 (4 real estate).wav": ["Sure, I can check it out.", "I'm a bit busy right now.", "Maybe later, I'm in the middle of something."],
    "Agent #1 (4 technology).wav": ["Sure, I can check it out.", "I'm a bit busy right now.", "Maybe later, I'm in the middle of something."],
    "Agent #1 (4 telecommunications).wav": ["Sure, I can check it out.", "I'm a bit busy right now.", "Maybe later, I'm in the middle of something."],
    "Agent #1 (4 transportation).wav": ["Sure, I can check it out.", "I'm a bit busy right now.", "Maybe later, I'm in the middle of something."],
    "Agent #1 (4 home services).wav": ["Sure, I can check it out.", "I'm a bit busy right now.", "Maybe later, I'm in the middle of something."],
    "Agent #1 (4 healthcare).wav": ["Sure, I can check it out.", "I'm a bit busy right now.", "Maybe later, I'm in the middle of something."],
    "Agent #1 (4 artificial intelligence).wav": ["Sure, I can check it out.", "I'm a bit busy right now.", "Maybe later, I'm in the middle of something."],
    "Agent #1 (4 AI).wav": ["Sure, I can check it out.", "I'm a bit busy right now.", "Maybe later, I'm in the middle of something."],
    "Agent #1 (4 manufacturing).wav": ["Sure, I can check it out.", "I'm a bit busy right now.", "Maybe later, I'm in the middle of something."],
    "Agent #1 (4 farming).wav": ["Sure, I can check it out.", "I'm a bit busy right now.", "Maybe later, I'm in the middle of something."],
    "Agent #1 (17).wav": ["I need web design services.", "I'm looking for mobile app development.", "I need help with digital marketing."],
    "Agent #1 (23 web design).wav": ["Tomorrow at 10 AM works for me.", "How about next Monday?", "I'm available this Friday."],
    "Agent #1 (23 mobile app development).wav": ["Tomorrow at 10 AM works for me.", "How about next Monday?", "I'm available this Friday."],
    "Agent #1 (23 digital marketing).wav": ["Tomorrow at 10 AM works for me.", "How about next Monday?", "I'm available this Friday."],
    "Agent #1 (23 animation).wav": ["Tomorrow at 10 AM works for me.", "How about next Monday?", "I'm available this Friday."],
    "Agent #1 (23 virtual assistance).wav": ["Tomorrow at 10 AM works for me.", "How about next Monday?", "I'm available this Friday."],
    "Agent #1 (23 branding).wav": ["Tomorrow at 10 AM works for me.", "How about next Monday?", "I'm available this Friday."],
    "Agent #1 (23 email marketing).wav": ["Tomorrow at 10 AM works for me.", "How about next Monday?", "I'm available this Friday."],
    "Agent #1 (23 web development).wav": ["Tomorrow at 10 AM works for me.", "How about next Monday?", "I'm available this Friday."],
    "Agent #1 (28 sample 1).wav": ["Sounds good, thank you.", "I'll be waiting for your call.", "Thank you, see you tomorrow."],
    "Agent #1 (28 sample 2).wav": ["Sounds good, thank you.", "I'll be waiting for your call.", "Thank you, see you on Thursday."],
    "Agent #1 (28 sample 3).wav": ["Sounds good, thank you.", "I'll be waiting for your call.", "Thank you, see you on Tuesday."],
    "Agent #1 (24).wav": ["That works for me.", "Sure, I'll be available.", "Okay, see you then."],
    "Agent #1 (25).wav": ["That works for me.", "Sure, I'll be available.", "Okay, see you then."],
    "Agent #1 (29).wav": ["That works for me.", "Sure, I'll be available.", "Okay, see you then."],
    "Q 3&4 rebuttals 6.wav": ["Sure, I can check it out.", "I'm a bit busy right now.", "Maybe later, I'm in the middle of something."],
    "Q 3&4 rebuttals 21.wav": ["That's true.", "I agree.", "Yes, that's correct."],
    "Q 3&4 rebuttals 9 (IF NO).wav": ["Yes, there are a few tasks.", "Not really.", "I'm not sure."],
    "Q 3&4 rebuttals 34.wav": ["I need to reroute my main website.", "I'm not sure yet.", "I need to think about it."],
    "Q 3&4 rebuttals 36.wav": ["I'm working on a new website.", "I'm developing a mobile app.", "I'm focusing on digital marketing."],
    "Q 3&4 rebuttals 12.wav": ["I'm planning to launch a new campaign.", "I'm not sure yet.", "I need to think about it."],
    "Q 3&4 rebuttals 32.wav": ["That's concerning.", "I need to work on that.", "Thanks for letting me know."],
    "Q 3&4 rebuttals 23.wav": ["That's great to hear.", "Good to know.", "Thanks for the information."],
    "Q 3&4 rebuttals 7.wav": ["Sure, I can check it out.", "I'm a bit busy right now.", "Maybe later, I'm in the middle of something."],
    "Q 3&4 rebuttals 29.wav": ["Great.", "Good to know.", "Thanks for the update."],
    "Q 3&4 rebuttals 38.wav": ["I'll check them out.", "Thanks for letting me know.", "Good to know."],
    "Q 3&4 rebuttals 28.wav": ["That's impressive.", "Good to know.", "Thanks for the information."],
    "Q 3&4 rebuttals 33.wav": ["I'm struggling with web design.", "I need help with marketing.", "I'm having trouble with development."],
    "Q 3&4 rebuttals 9 (beginning and IF YES).wav": ["Yes, I did.", "No, I didn't.", "I'm not sure yet."],
    "Q 3&4 rebuttals 26.wav": ["I didn't know that.", "Thanks for letting me know.", "I'll look into that."],
    "Q 3&4 rebuttals 11.wav": ["I need to finalize the design.", "I need to develop the content.", "I need to set up the infrastructure."],
    "Agent #1 (16).wav": ["Okay, I see it.", "Got it, thanks.", "I found it."],
    "Agent #1 (15).wav": ["Okay, I see it.", "Got it, thanks.", "I found it."],
    "Agent #1 (6).wav": ["I'm there.", "Okay, I'm on the page.", "I have it open."],
    "Agent #1 (9).wav": ["I'm on the page.", "I see the reviews.", "I'm watching the video."],
    "Agent #1 (8).wav": ["I'm on the page.", "I see the reviews.", "I'm watching the video."],
    "Agent #1 (19).wav": ["Okay.", "Sure.", "Alright."],
    "Agent #1 (11).wav": ["Okay.", "Sure.", "Alright."],
    "Agent #1 (12).wav": ["Okay.", "Sure.", "Alright."],
    "Agent #1 (13).wav": ["Okay, I'll watch it later.", "Got it, thanks.", "I'll check it out after the call."],
    "Agent #1 (14).wav": ["Okay, I'll watch it later.", "Got it, thanks.", "I'll check it out after the call."],
    "Agent #1 (18).wav": ["My name is John.", "I'm Sarah.", "It's Michael."],
    "Agent #1 (21).wav": ["Okay.", "Sure.", "Alright."],
    "Rebuttals row 15 part 1.wav": ["I'm at my computer.", "Okay, I'm on the page.", "I see the services button."],
    "Rebuttals row 15 part 2.wav": ["I'm at my computer.", "Okay, I'm on the page.", "I see the services button."],
    "Rebuttals row 15 part 3.wav": ["I'm at my computer.", "Okay, I'm on the page.", "I see the services button."],
    "Incoming call voicemail box message (Rebuttals 4G).wav": ["Thank you.", "I'll check the website.", "Got it, thanks."],
    "Voicemail drop (Rebuttals 4C).wav": ["Thank you.", "I'll check the website.", "Got it, thanks."],
    "Gatekeepers _ (row 33).wav": ["He's not available.", "Can I take a message?", "He's in a meeting."],
    "Gatekeepers 1.wav": ["She's not available.", "Can I take a message?", "She's in a meeting."],
    "Gatekeepers 2.wav": ["He's not available.", "Can I take a message?", "He's in a meeting."],
    "Gatekeepers 3.wav": ["He's not available.", "Can I take a message?", "He's in a meeting."],
    "1. Sorry, what was that_.wav": ["Sorry, what was that?", "Can you repeat that?", "I didn't catch that."],
    "2. Say that again_.wav": ["Sorry, what was that?", "Can you repeat that?", "I didn't catch that."],
    "3. I didn’t catch that..wav": ["Sorry, what was that?", "Can you repeat that?", "I didn't catch that."],
    "4. Sorry, one more time_.wav": ["Sorry, what was that?", "Can you repeat that?", "I didn't catch that."],
    "5. What was that_.wav": ["Sorry, what was that?", "Can you repeat that?", "I didn't catch that."],
    "6. I missed that..wav": ["Sorry, what was that?", "Can you repeat that?", "I didn't catch that."],
    "7. Pardon me_.wav": ["Sorry, what was that?", "Can you repeat that?", "I didn't catch that."],
    "1. sony47821.com.wav": ["Sony 47821 cam", "Sony 47821 dot com", "Sony 47821 website"],
    "2. bcraccounting.com.wav": ["BCR accounting.com", "BCR accounting dot com", "BCR accounting website"],
    "3. yummy-cookies.com.wav": ["yummy Dash cookies.com", "yummy Dash cookies dot com", "yummy Dash cookies website"],
    "4. burbys.com.wav": ["furbies.com", "furbies dot com", "furbies website"],
    "5. wbrf.com.wav": ["wbrf cam", "wbrf dot com", "wbrf website"],
    "6. 24-7auto.com.wav": ["24 dash 7 auto.com", "24 dash 7 auto dot com", "24 dash 7 auto website"],
    "7. kprmusic.org.wav": ["kpr music.org", "kpr music dot org", "kpr music website"],
    "8. klaxxon.edu.wav": ["collects on EDU", "collects on dot EDU", "collects on website"],
    "9. fbi.gov.wav": ["fbi.gov", "fbi dot gov", "fbi website"],
    "10. google.us.wav": ["Google us", "Google dot us", "Google website"]
}

# Initialize conversation state
conversation_state = {
    "current_key": None,
    "previous_key": None,
    "recognized_text": None,
    "matched_key": None,
    "context": [],
    "history": []
}

# Initialize SignalWire client
client = SignalWireClient(SIGNALWIRE_PROJECT_ID, SIGNALWIRE_API_TOKEN, signalwire_space_url=SIGNALWIRE_SPACE_URL)

def make_call():
    call = client.calls.create(
        to=LEAD_PHONE_NUMBER,
        from_=SIGNALWIRE_PHONE_NUMBER,
        url="http://your-server-url/answer"
    )
    return call.sid

def recognize_speech_from_mic():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        logging.info("Listening...")
        audio = recognizer.listen(source)

    try:
        response = recognizer.recognize_google(audio)
        logging.info(f"Recognized: {response}")
        return response
    except sr.UnknownValueError:
        logging.error("Sorry, I did not understand that.")
        return None
    except sr.RequestError:
        logging.error("Sorry, my speech service is down.")
        return None

def match_response(recognized_text, potential_responses, threshold=80):
    recognized_text = recognized_text.lower().strip()
    best_match = None
    highest_similarity = 0
    for key, responses in potential_responses.items():
        for response in responses:
            similarity = fuzz.ratio(recognized_text, response.lower().strip())
            if similarity >= threshold and similarity > highest_similarity:
                best_match = key
                highest_similarity = similarity
    if best_match:
        logging.info(f"Matched key: {best_match} with similarity: {highest_similarity}")
    return best_match

def play_audio(file_path):
    audio = AudioSegment.from_wav(file_path)
    play(audio)

def update_conversation_state(state, recognized_text, matched_key):
    state["previous_key"] = state["current_key"]
    state["current_key"] = matched_key
    state["recognized_text"] = recognized_text
    state["matched_key"] = matched_key
    # Update context based on the matched key
    if matched_key:
        state["context"].append(transcriptions[matched_key])
    # Update history with timestamp
    state["history"].append({
        "timestamp": datetime.now().isoformat(),
        "recognized_text": recognized_text,
        "matched_key": matched_key,
        "agent_response": transcriptions[matched_key] if matched_key else None
    })

def get_fallback_response():
    return "I'm sorry, I didn't catch that. Could you please repeat?"

def handle_call():
    while True:
        recognized_text = recognize_speech_from_mic()
        if recognized_text:
            matched_key = match_response(recognized_text, potential_responses)
            if matched_key:
                audio_file_path = os.path.join(AUDIO_FOLDER, matched_key)
                if os.path.exists(audio_file_path):
                    play_audio(audio_file_path)
                    update_conversation_state(conversation_state, recognized_text, matched_key)
                else:
                    logging.error(f"Audio file {audio_file_path} not found.")
            else:
                logging.warning("No matching response found.")
                fallback_response = get_fallback_response()
                logging.info(f"Agent: {fallback_response}")
                update_conversation_state(conversation_state, recognized_text, None)
        else:
            logging.warning("No speech recognized.")

if __name__ == "__main__":
    call_sid = make_call()
    logging.info(f"Call initiated with SID: {call_sid}")
    handle_call()