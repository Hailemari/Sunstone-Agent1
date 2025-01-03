# How to do these in my current implementation

"""
Manage Conversation Context:

Maintain the context of the conversation to provide relevant responses.
Use session variables or context objects to store conversation state

Design a Decision Tree/Flow:

Create a decision tree or flowchart to handle the conversation logic.
Map user intents to specific actions and responses.

Handle Edge Cases and Errors:

Implement error handling and fallback mechanisms for unexpected inputs.
Provide graceful responses for unrecognized intents.
"""


class DecisionTree:
    def __init__(self):
        self.tree = {
            "greeting": {
                "message": "Hi [LEAD'S NAME], this is [MARC]. How are you?",
                "options": {
                    "good": "positive_response",
                    "not_good": "negative_response",
                    "ask_about_services": "ask_about_services",
                },
            },
            "positive_response": {
                "message": "You recently purchased [LEAD'S WEBSITE]. Is there a project behind this?",
                "options": {
                    "yes": "project_yes",
                    "no": "project_no",
                },
            },
            "negative_response": {
                "message": "I am sorry to hear that. You recently purchased [LEAD'S WEBSITE]. Is there a project behind this?",
                "options": {
                    "yes": "project_yes",
                    "no": "project_no",
                },
            },
            "ask_about_services": {
                "message": "We offer a variety of services including web design, mobile app development, and digital marketing. Which one are you interested in?",
                "options": {
                    "web_design": "service_web_design",
                    "mobile_app": "service_mobile_app",
                    "digital_marketing": "service_digital_marketing",
                },
            },
            "service_web_design": {
                "message": "Great! I will transfer you to my manager, who is an expert in web design.",
            },
            "service_mobile_app": {
                "message": "Great! I will transfer you to my manager, who is an expert in mobile app development.",
            },
            "service_digital_marketing": {
                "message": "Great! I will transfer you to my manager, who is an expert in digital marketing.",
            },
            # more nodes ...
        }

    def get_response(self, node, user_input):
        if node not in self.tree:
            return None, "Sorry, I didn't understand that."

        current_node = self.tree[node]
        message = current_node["message"]
        options = current_node.get("options", {})

        if user_input in options:
            next_node = options[user_input]
            return next_node, message
        else:
            return None, message