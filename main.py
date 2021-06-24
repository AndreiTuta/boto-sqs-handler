import json
import requests
import urllib


class SendinblueHandler:
    def __init__(self, key):
        self.contact_url = "https://api.sendinblue.com/v3/contacts/"
        self.email_url = "https://api.sendinblue.com/v3/smtp/email"

        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "api-key": key,
        }

    def make_sendinblue_message(
            self, email: str, name: str, event: int) -> bool:
        print(f"Processing new Sendinblue email for {email} and event {event}")
        payload = {
            "to": [{"email": email, "name": name}], 
            # use the templateId for event
            "templateId": event
        }

        response = requests.request(
            "POST", self.email_url, json=payload, headers=self.headers)

        self.check_create_sendinblue_contact(email, name)
        print(response.text)
        return response.status_code == 200

    def check_sendinblue_contact(self, email: str) -> bool:
        print(
            f"Searching for Sendinblue for Sendinblue contact with email {email}")
        response = requests.request(
            "GET", self.contact_url + email, headers=self.headers)
        print(response.text)
        return response.status_code == 404

    def check_create_sendinblue_contact(self, email: str, name: str) -> bool:
        if(self.check_sendinblue_contact(urllib.parse.quote(email))):
            print(
                f"No contact found with email address {email}. Creating a new Sendinblue contact for {name}")
            self.make_sendinblue_contact(email, name)
        else:
            print(
                f"Contact with email {email} already exists. Skipping creating a contact")

    def make_sendinblue_contact(self, email: str, name: str) -> bool:
        payload = {
            "attributes": {"FIRSTNAME": name},
            "listIds": [3],
            "updateEnabled": False,
            "email": email,
        }

        response = requests.request(
            "POST", self.contact_url, json=payload, headers=self.headers)
        print(response.text)
        return response.status_code == 200

    # {"name": name to show in email,"email": address to send email to , "subject": text to show as subject of the email,"isContact": boolean for only creating a contact via sendinblue, "event": template Id to be used when sending an email. }
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


def lambda_handler(event, context):
    response = event['Records']
    sqs_handler = SendinblueHandler(
        "API-key")
    for entry in response:
        print(
            f"Processing SQS message with id: {entry['messageId']} and body: {entry['body']})")
        try:
            success = sqs_handler.process_message(entry['body'])
        except Exception as e:
            print(f"exception while processing message: {repr(e)}")
            continue
