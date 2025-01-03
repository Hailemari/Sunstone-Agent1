import random
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Load NLP model
nlp = spacy.load("en_core_web_sm")

training_data = [
    ("I'm good, thanks. How are you?", "greeting_response"),
    ("I'm fine, thank you. How about you?", "greeting_response"),
    ("Doing well, thanks for asking.", "greeting_response"),
    ("It's for the e-commerce industry.", "industry_response"),
    ("I'm in the healthcare industry.", "industry_response"),
    ("It's for a tech startup.", "industry_response"),
]

# Train intent recognition model
vectorizer = TfidfVectorizer()
X_train = vectorizer.fit_transform([text for text, label in training_data])
Y_train = [label for text, label in training_data]
intent_model = LogisticRegression()
intent_model.fit(X_train, Y_train)

# Decision tree with dynamic responses
decision_tree = {
    "Agent #1 (1).wav": {
        "agent": "hi John it's Olivia how are you",
        "responses": {
            "greeting_response": ["Agent #1 (3).wav"]
        }
    },
    "Agent #1 (3).wav": {
        "agent": "I'm calling from a high-performance marketing agency here in New York that are also experts in web design mobile app development along with other business services what industry is this for",
        "responses": {
            "industry_response": ["Agent #1 (4 ecommerce).wav", "Agent #1 (4 healthcare).wav", "Agent #1 (4 technology).wav"]
        }
    },
    # Add more nodes here following the same structure
}
# Example training data for intent recognition
# Function to predict intent 
def predict_intent(text):
    X_test = vectorizer.transform([text])
    return intent_model.predict(X_test)[0]

# Function to play audio
def play_audio(file_path):
    print(f"Playing audio: {file_path}")

# Function to traverse decision tree
def traverse_decision_tree(tree, current_node, lead_response, history):
    if current_node not in tree:
        print("End of conversation.")
        return None

    node = tree[current_node]
    agent_message = node["agent"]
    print(f"Agent: {agent_message}")

    # Add the current step to the history
    history.append({
        "agent": agent_message,
        "lead": lead_response
    })

    # Predict intent
    intent = predict_intent(lead_response)
    if intent in node["responses"]:
        next_audio = random.choice(node["responses"][intent])
        play_audio(next_audio)
        return next_audio
    else:
        print("Invalid response.")
        return None

# Example usage
current_node = "Agent #1 (1).wav"
history = []

while current_node:
    lead_response = input("Lead: ")
    current_node = traverse_decision_tree(decision_tree, current_node, lead_response, history)

# Print the conversation history
print("Conversation History:")
for step in history:
    print(f"Agent: {step['agent']}")
    print(f"Lead: {step['lead']}")