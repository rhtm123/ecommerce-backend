import os
import json
import threading
from twilio.rest import Client
from decouple import config

def send_wa_msg(content_template_sid, variables, receiver):
    """
    Function to send WhatsApp messages via Twilio in a background thread.
    """

    def send_message(content_template_sid, variables, receiver):
        account_sid = config('TWILIO_ACCOUNT_SID')
        auth_token = config('TWILIO_AUTH_TOKEN')
        sender = config('TWILIO_SENDER_NUMBER')

        if receiver:
            if receiver.startswith("0"):
                receiver = receiver[1:]

            if not receiver.startswith("+91"):
                receiver = "+91" + receiver

            client = Client(account_sid, auth_token)
            variables_json = json.dumps(variables)  # Convert dictionary to JSON string

            try:
                message = client.messages.create(
                    from_=f'whatsapp:{sender}',  # Twilio's WhatsApp number
                    to=f'whatsapp:{receiver}',  # Recipient's WhatsApp number
                    content_sid=content_template_sid,
                    content_variables=variables_json,
                )

                print(f"Message sent! SID: {message.sid}")
            except Exception as e:
                print(f"Error sending message: {e}")

    # Run the send_message function in a background thread
    thread = threading.Thread(target=send_message, args=(content_template_sid, variables, receiver))
    thread.daemon = True  # Ensures the thread exits when the main program exits
    thread.start()

    return "Message sending started in background."

# Example Usage: