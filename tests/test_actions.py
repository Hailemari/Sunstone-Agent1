import unittest
from unittest.mock import patch, MagicMock
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Tracker
from actions.actions import (
    ActionSendInfo,
    ActionScheduleCallback,
    ActionProvideServiceInstructions,
    ActionConfirmService,
    ActionAskPricing,
    ActionHandleSmallTalk,
    ActionCompleteTask,
    ActionHandleHelpRequest
)

class TestActions(unittest.TestCase):

    def setUp(self):
        self.dispatcher = CollectingDispatcher()
        self.tracker = Tracker(sender_id='default', slots={}, latest_message={}, events=[], paused=False)
        self.domain = {}

    def test_action_send_info(self):
        action = ActionSendInfo()
        self.tracker.slots['email'] = 'test@example.com'
        events = action.run(self.dispatcher, self.tracker, self.domain)
        self.assertEqual(len(events), 0)
        self.assertEqual(self.dispatcher.messages[0]['text'], 'Sure, I will send the information to test@example.com.')
        print("ActionSendInfo test passed.")

    def test_action_send_info_no_email(self):
        action = ActionSendInfo()
        self.tracker.slots['email'] = None
        events = action.run(self.dispatcher, self.tracker, self.domain)
        self.assertEqual(len(events), 0)
        self.assertEqual(self.dispatcher.messages[0]['text'], "I couldn't find your email. Could you please provide it?")
        print("ActionSendInfo no email test passed.")

    def test_action_schedule_callback(self):
        action = ActionScheduleCallback()
        self.tracker.slots['callback_time'] = 'tomorrow at 3 PM'
        events = action.run(self.dispatcher, self.tracker, self.domain)
        self.assertEqual(len(events), 0)
        self.assertEqual(self.dispatcher.messages[0]['text'], "Great! I've scheduled a callback for tomorrow at 3 PM.")
        print("ActionScheduleCallback test passed.")

    def test_action_schedule_callback_no_time(self):
        action = ActionScheduleCallback()
        self.tracker.slots['callback_time'] = None
        events = action.run(self.dispatcher, self.tracker, self.domain)
        self.assertEqual(len(events), 0)
        self.assertEqual(self.dispatcher.messages[0]['text'], "When would you like to schedule the callback?")
        print("ActionScheduleCallback no time test passed.")

    def test_action_provide_service_instructions(self):
        action = ActionProvideServiceInstructions()
        self.tracker.slots['device'] = 'computer'
        events = action.run(self.dispatcher, self.tracker, self.domain)
        self.assertEqual(len(events), 0)
        self.assertEqual(self.dispatcher.messages[0]['text'], "On your computer, please hover over the SERVICES button at the top of our homepage.")
        print("ActionProvideServiceInstructions test passed.")

    def test_action_confirm_service(self):
        action = ActionConfirmService()
        self.tracker.slots['selected_service'] = 'web design'
        events = action.run(self.dispatcher, self.tracker, self.domain)
        self.assertEqual(len(events), 0)
        self.assertEqual(self.dispatcher.messages[0]['text'], "Great choice! Let me know if you need more details about web design.")
        print("ActionConfirmService test passed.")

    def test_action_ask_pricing(self):
        action = ActionAskPricing()
        events = action.run(self.dispatcher, self.tracker, self.domain)
        self.assertEqual(len(events), 0)
        self.assertEqual(self.dispatcher.messages[0]['text'], "We have various pricing options listed under each service. Let me guide you to our pricing page.")
        print("ActionAskPricing test passed.")

    def test_action_handle_small_talk(self):
        action = ActionHandleSmallTalk()
        self.tracker.latest_message = {'text': 'Tell me about politics'}
        events = action.run(self.dispatcher, self.tracker, self.domain)
        self.assertEqual(len(events), 0)
        self.assertEqual(self.dispatcher.messages[0]['text'], "I try not to keep up with politics. Things are too crazy these days.")
        print("ActionHandleSmallTalk test passed.")

    def test_action_complete_task(self):
        action = ActionCompleteTask()
        events = action.run(self.dispatcher, self.tracker, self.domain)
        self.assertEqual(len(events), 0)
        self.assertEqual(self.dispatcher.messages[0]['text'], "Excellent! Let’s move on to the next step.")
        print("ActionCompleteTask test passed.")

    def test_action_handle_help_request(self):
        action = ActionHandleHelpRequest()
        events = action.run(self.dispatcher, self.tracker, self.domain)
        self.assertEqual(len(events), 0)
        self.assertEqual(self.dispatcher.messages[0]['text'], "Of course! What specific assistance do you need?")
        print("ActionHandleHelpRequest test passed.")

if __name__ == '__main__':
    unittest.main()