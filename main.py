import json
import requests
import urllib


class SendinblueHandler:
    def __init__(self, key):
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "api-key": key,
        }

    def make_sendinblue_message(
            self, email: str, name: str, event: int) -> bool:
        url = "https://api.sendinblue.com/v3/smtp/email"

        payload = {
            "to": [{"email": email, "name": name}], "replyTo": {"email": "no-reply@welcometogate.com"},
            # use the templateId for event
            "templateId": event
        }

        response = requests.request(
            "POST", url, json=payload, headers=self.headers)

        self.check_create_sendinblue_contact(email, name)
        print(response.text)
        return response.status_code == 200

    def check_sendinblue_contact(self, email: str) -> bool:
        url = "https://api.sendinblue.com/v3/contacts/" + email
        response = requests.request("GET", url, headers=self.headers)
        print(response.text)
        return response.status_code == 404

    def check_create_sendinblue_contact(self, email: str, name: str) -> bool:
        if(self.check_sendinblue_contact(urllib.parse.quote(email))):
            self.make_sendinblue_contact(email, name)
        else:
            print(
                f"Contact with email {email} already exists. Skipping creating a contact")

    def make_sendinblue_contact(self, email: str, name: str) -> bool:
        url = "https://api.sendinblue.com/v3/contacts"

        payload = {
            "attributes": {"FIRSTNAME": name},
            "listIds": [3],
            "updateEnabled": False,
            "email": email,
        }

        response = requests.request(
            "POST", url, json=payload, headers=self.headers)
        print(response.text)
        return response.status_code == 200

    # {"name": name to show in email,"email": address to send email to , "subject": text to show as subject of the email,"isContact": boolean for only creating a contact via sendinblue}
    def process_message(
        self, sqs_message: dict,
    ) -> None:
        if sqs_message["isContact"] == False:
            print(
                f"Processing message as an email"
            )
            self.make_sendinblue_message(
                sqs_message["email"], sqs_message["name"], sqs_message["event"]
            )
        else:
            print(
                f"Processing message as a contact"
            )
            self.check_create_sendinblue_contact(
                sqs_message["email"], sqs_message["name"]
            )


class Message():
    def __init__(self, id, body):
        self.id = id
        self.body = body
        print(f"Processing new sqs message with id: {id} and body: {body}")


def lambda_handler(event, context):
    response = event['Records']
    sqs_handler = SendinblueHandler(
        "API-key")
    for entry in response:
        m = Message(entry['messageId'], entry['body'])
        try:
            success = sqs_handler.process_message(m.body)
        except Exception as e:
            print(f"exception while processing message: {repr(e)}")
            continue