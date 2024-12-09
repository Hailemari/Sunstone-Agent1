from flask import Flask, request, Response

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    # Log the incoming call details (optional)
    from_number = request.form.get("From")
    to_number = request.form.get("To")
    call_sid = request.form.get("CallSid")
    print(f"Incoming call from {from_number} to {to_number}, Call SID: {call_sid}")

    # Return an empty TwiML response
    response = "<Response></Response>"
    return Response(response, mimetype="text/xml")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
