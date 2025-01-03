from flask import Flask, request, Response, jsonify
import requests

app = Flask(__name__)

# Dictionary to store call statuses
call_status = {}

# Dictionary to store conversation details
conversations = {}

@app.route("/webhook", methods=["POST"])
def webhook():
    # Log the incoming call details (optional)
    from_number = request.form.get("From")
    to_number = request.form.get("To")
    call_sid = request.form.get("CallSid")
    print(f"Incoming call from {from_number} to {to_number}, Call SID: {call_sid}")

    # Initialize conversation details
    conversations[call_sid] = {
        "from": from_number,
        "to": to_number,
        "messages": []
    }

    # Respond with LaML to answer the call and play a message
    response = """
    <Response>
        <Say>Thank you for calling. Please hold while we connect you.</Say>
        <Pause length="2"/>
        <Say>This is a test call from SignalWire.</Say>
    </Response>
    """
    return Response(response, mimetype="text/xml")

@app.route("/call_status", methods=["POST"])
def call_status_update():
    data = request.form
    call_sid = data.get('CallSid')
    status = data.get('CallStatus')
    call_status[call_sid] = status
    print(f"Call SID: {call_sid}, Status: {status}")

    # If the call is completed, post the conversation to the CRM
    if status == "completed":
        post_conversation_to_crm(call_sid)

    return jsonify({'status': 'received'})

def post_conversation_to_crm(call_sid):
    conversation = conversations.get(call_sid)
    if not conversation:
        print(f"No conversation found for Call SID: {call_sid}")
        return

    crm_endpoint = "https://crm-endpoint.com/api/conversations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer api_token"
    }
    response = requests.post(crm_endpoint, json=conversation, headers=headers)

    if response.status_code == 200:
        print(f"Successfully posted conversation for Call SID: {call_sid} to CRM")
    else:
        print(f"Failed to post conversation for Call SID: {call_sid} to CRM. Status code: {response.status_code}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)