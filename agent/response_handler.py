def handle_responses(agent_responses, play_audio_from_s3):
    """
    Process agent responses and play the corresponding audio file.

    Args:
        agent_responses (list): List of responses from the Rasa agent.
        play_audio_from_s3 (function): Function to play audio from S3.
    """
    for response in agent_responses:
        response_text = response.get("text", "").lower()

        if "hi" in response_text or "hello" in response_text:
            play_audio_from_s3("greeting.mp3")
        elif "you recently purchased" in response_text:
            play_audio_from_s3("positive_response.mp3")
        elif "i’m sorry to hear that" in response_text:
            play_audio_from_s3("negative_response.mp3")
        elif "i’m calling from sunstone digital" in response_text:
            play_audio_from_s3("who_are_you.mp3")
        elif "we noticed you recently purchased" in response_text:
            play_audio_from_s3("what_do_you_want.mp3")
        elif "that's understandable" in response_text:
            play_audio_from_s3("not_interested.mp3")
        elif "i get it" in response_text:
            play_audio_from_s3("dont_have_time.mp3")
        elif "our services are designed to provide high roi" in response_text:
            play_audio_from_s3("too_expensive.mp3")
        elif "absolutely, i can give you time" in response_text:
            play_audio_from_s3("need_to_think.mp3")
        elif "sure, i’ll email you more details" in response_text:
            play_audio_from_s3("send_info.mp3")
        elif "we saw you recently purchased" in response_text:
            play_audio_from_s3("why_calling.mp3")
        elif "what projects are you working on" in response_text:
            play_audio_from_s3("other_projects.mp3")
        elif "that’s okay" in response_text:
            play_audio_from_s3("dont_own_business.mp3")
        elif "we’re experts in digital marketing" in response_text:
            play_audio_from_s3("what_do_you_do.mp3")
        elif "great! which service caught your attention" in response_text:
            play_audio_from_s3("finished_video.mp3")
        elif "on your computer" in response_text:
            play_audio_from_s3("service_instructions_computer.mp3")
        elif "on your phone" in response_text:
            play_audio_from_s3("service_instructions_phone.mp3")
        elif "no problem. when would be a convenient time" in response_text:
            play_audio_from_s3("schedule_callback.mp3")
        elif "i enjoy staying productive and reading" in response_text:
            play_audio_from_s3("general_small_talk.mp3")
        elif "could you please connect me with" in response_text:
            play_audio_from_s3("gatekeeper.mp3")
        elif "i apologize for the mistake" in response_text:
            play_audio_from_s3("incorrect_number.mp3")
        elif "i understand. can i call you back" in response_text:
            play_audio_from_s3("driving.mp3")
        elif "no worries. when would be a better time" in response_text:
            play_audio_from_s3("busy.mp3")
        elif "let’s lock in another time" in response_text:
            play_audio_from_s3("reschedule.mp3")
        elif "excellent! let’s proceed to the next step" in response_text:
            play_audio_from_s3("finished_task.mp3")
        elif "we specialize in web development" in response_text:
            play_audio_from_s3("inquire_specific_service.mp3")
        elif "thank you for your time" in response_text:
            play_audio_from_s3("end_call.mp3")
        elif "how’s your business performing" in response_text:
            play_audio_from_s3("ask_about_business.mp3")
        elif "what are the main challenges" in response_text:
            play_audio_from_s3("objection_response.mp3")
        elif "based on your needs" in response_text:
            play_audio_from_s3("recommend_services.mp3")
        elif "let’s go through a short video" in response_text:
            play_audio_from_s3("watch_video.mp3")
        elif "sure, take your time" in response_text:
            play_audio_from_s3("pause_conversation.mp3")
        elif "what specific expertise are you looking for" in response_text:
            play_audio_from_s3("ask_for_expertise.mp3")
        elif "of course! what specific assistance" in response_text:
            play_audio_from_s3("need_help.mp3")
        elif "that's the service i need" in response_text:
            play_audio_from_s3("confirm_service.mp3")
        elif "what’s the cost" in response_text:
            play_audio_from_s3("ask_pricing.mp3")
        elif "task done" in response_text:
            play_audio_from_s3("completed_task.mp3")
        else:
            play_audio_from_s3("small_talk_general.mp3")