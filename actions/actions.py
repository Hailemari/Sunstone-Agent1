from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ActionSendInfo(Action):

    def name(self) -> Text:
        return "action_send_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        email = tracker.get_slot("email")
        if email:
            dispatcher.utter_message(text=f"Sure, I will send the information to {email}.")
            return []
        else:
            dispatcher.utter_message(text="I couldn't find your email. Could you please provide it?")
            return []

class ActionScheduleCallback(Action):

    def name(self) -> Text:
        return "action_schedule_callback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        callback_time = tracker.get_slot("callback_time")
        if callback_time:
            dispatcher.utter_message(text=f"Great! I've scheduled a callback for {callback_time}.")
            return []
        else:
            dispatcher.utter_message(text="When would you like to schedule the callback?")
            return []

class ActionProvideServiceInstructions(Action):

    def name(self) -> Text:
        return "action_provide_service_instructions"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        device = tracker.get_slot("device")
        if device == "computer":
            dispatcher.utter_message(text="On your computer, please hover over the SERVICES button at the top of our homepage.")
        elif device == "phone":
            dispatcher.utter_message(text="On your phone, click the three horizontal lines at the top right corner, and then select SERVICES.")
        else:
            dispatcher.utter_message(text="Please navigate to the SERVICES section on our website.")
        return []

class ActionConfirmService(Action):

    def name(self) -> Text:
        return "action_confirm_service"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        service = tracker.get_slot("selected_service")
        if service:
            dispatcher.utter_message(text=f"Great choice! Let me know if you need more details about {service}.")
        else:
            dispatcher.utter_message(text="Could you specify which service you’re interested in?")
        return []

class ActionAskPricing(Action):

    def name(self) -> Text:
        return "action_ask_pricing"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="We have various pricing options listed under each service. Let me guide you to our pricing page.")
        return []

class ActionHandleSmallTalk(Action):

    def name(self) -> Text:
        return "action_handle_small_talk"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        topic = tracker.latest_message.get('text')
        if "politics" in topic.lower():
            dispatcher.utter_message(text="I try not to keep up with politics. Things are too crazy these days.")
        elif "weather" in topic.lower():
            dispatcher.utter_message(text="I’m just staying inside today. It’s relaxing.")
        else:
            dispatcher.utter_message(text="I enjoy reading and relaxing indoors when I get the chance.")
        return []

class ActionCompleteTask(Action):

    def name(self) -> Text:
        return "action_complete_task"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Excellent! Let’s move on to the next step.")
        return []

class ActionHandleHelpRequest(Action):

    def name(self) -> Text:
        return "action_handle_help_request"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Of course! What specific assistance do you need?")
        return []