import json
import threading
from twilio.rest import Client
from decouple import config

import plivo
from plivo.utils.template import Template

# AUTH_ID=config('PLIVO_AUTH_ID') 
# AUTH_TOKEN=config('PLIVO_AUTH_TOKEN')
# PLIVO_SENDER_NUMBER=config('PLIVO_SENDER_NUMBER')

from estores.models import WhatsAppCredential


def send_wa_msg_plivo(template_id, template_parameters, receiver, estore_id=None):
    """
    Function to send WhatsApp messages via Plivo in a background thread.
    """

    def send_message(template_id, template_parameters, receiver):

        wa_credentials = WhatsAppCredential.objects.filter(estore_id=estore_id, is_active=True, sender_name="plivo")

        if not wa_credentials.exists():
            print("No WhatsApp credentials found for this eStore.")
            return
        
        wa_credential = wa_credentials.first()

        # print("WhatsApp Credential:", wa_credential)
        # print(wa_credential.templates)

        template_name = wa_credential.templates[template_id]

        AUTH_ID = wa_credential.auth_id
        AUTH_TOKEN = wa_credential.auth_token
        PLIVO_SENDER_NUMBER = wa_credential.sender_number

        # print(AUTH_ID, AUTH_TOKEN, PLIVO_SENDER_NUMBER)
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
    thread = threading.Thread(target=send_message, args=(template_id, template_parameters, receiver))
    thread.daemon = True  # Ensures the thread exits when the main program exits
    thread.start()

    return "Message sending started in background."


# Example Usage: