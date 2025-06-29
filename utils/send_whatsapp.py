import json
import threading
from twilio.rest import Client
from decouple import config

import plivo
from plivo.utils.template import Template

AUTH_ID=config('PLIVO_AUTH_ID') 
AUTH_TOKEN=config('PLIVO_AUTH_TOKEN')
PLIVO_SENDER_NUMBER=config('PLIVO_SENDER_NUMBER')


def send_wa_msg_plivo(template_name, template_parameters, receiver):
    """
    Function to send WhatsApp messages via Plivo in a background thread.
    """

    def send_message(template_name, template_parameters, receiver):
        client = plivo.RestClient(AUTH_ID, AUTH_TOKEN)

    
        if receiver:
            if receiver.startswith("0"):
                receiver = receiver[1:]
            if not receiver.startswith("+91"):
                receiver = "+91" + receiver

        template = Template(**{
            "name": template_name,
            "language": "en",
            "components": [
                {
                    "type": "body",
                    "parameters": [{"type": "text", "text": str(template_parameters[i])} for i in range(len(template_parameters))]
                }
            ]
        })

        try:
            response = client.messages.create(
                src=PLIVO_SENDER_NUMBER,
                dst=receiver,
                type_="whatsapp",
                template=template,
            )

            print(response)
            print("Message UUID:", response.message_uuid)
        except plivo.exceptions.PlivoRestError as e:
            print(f"Error: {e}")

    # Run the send_message function in a background thread
    thread = threading.Thread(target=send_message, args=(template_name, template_parameters, receiver))
    thread.daemon = True  # Ensures the thread exits when the main program exits
    thread.start()

    return "Message sending started in background."


def send_wa_msg(content_template_sid, variables, receiver):
    """
    Function to send WhatsApp messages via Twilio in a background thread.
    """

    def send_message(content_template_sid, variables, receiver):
        account_sid = config('TWILIO_ACCOUNT_SID')
        auth_token = config('TWILIO_AUTH_TOKEN')
        sender = config('TWILIO_SENDER_NUMBER')

        # print(sender);

        if receiver:
            if receiver.startswith("0"):
                receiver = receiver[1:]

            if not receiver.startswith("+91"):
                receiver = "+91" + receiver

            client = Client(account_sid, auth_token)
            variables_json = json.dumps(variables)  # Convert dictionary to JSON string

            try:
                # pass
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