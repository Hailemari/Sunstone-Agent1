from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import requests
from signalwire.rest import Client as SignalWireClient

app = FastAPI()

# Dictionary to store call statuses
call_status = {}

# Dictionary to store conversation details
conversations = {}

# SignalWire credentials
SIGNALWIRE_PROJECT_ID = "project_id"
SIGNALWIRE_API_TOKEN = "api_token"
SIGNALWIRE_SPACE_URL = "space_url"
SIGNALWIRE_PHONE_NUMBER = "signalwire_phone_number"

signalwire_client = SignalWireClient(SIGNALWIRE_PROJECT_ID, SIGNALWIRE_API_TOKEN, signalwire_space_url=SIGNALWIRE_SPACE_URL)

@app.post("/make_call")
async def make_call(to_number: str):
    try:
        call = signalwire_client.calls.create(
            from_=SIGNALWIRE_PHONE_NUMBER,
            to=to_number,
            url="https://your-ngrok-url/webhook" 
        )
        print(f"Call initiated to {to_number}. Call SID: {call.sid}")
        return JSONResponse(content={'status': 'call initiated', 'call_sid': call.sid})
    except Exception as e:
        print(f"Failed to initiate call: {e}")
        return JSONResponse(content={'status': 'failed to initiate call', 'error': str(e)}, status_code=500)

@app.post("/call_status")
async def call_status_update(request: Request):
    form = await request.form()
    call_sid = form.get('CallSid')
    status = form.get('CallStatus')
    call_status[call_sid] = status
    print(f"Call SID: {call_sid}, Status: {status}")

    # If the call is completed, post the conversation to the CRM
    if status == "completed":
        post_conversation_to_crm(call_sid)

    return JSONResponse(content={'status': 'received'})

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
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)