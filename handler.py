# will extend https://github.com/Pastromhaug/code_samples/blob/master/sqs_consumer/sqs_consumer.py
import time
import requests
import json
from signal import SIGINT, SIGTERM, signal

from datadog import statsd


class SendinblueHandler:
    def make_sendinblue_message(
        self, email: str, name: str, email_template: str, email_subject: str
    ) -> None:

        url = "https://api.sendinblue.com/v3/smtp/email"

        payload = {
            "sender": {"name": "Gate", "email": "noreply@atdev.com"},
            "to": [{"email": email, "name": name}],
            "replyTo": self.reply,
            "htmlContent": email_template,
            "subject": email_subject,
        }

        response = requests.request("POST", url, json=payload, headers=self.headers)

        print(response.text)
        self.make_sendinblue_contact(email, name)
        pass

    def make_sendinblue_contact(self, email: str, name: str) -> None:
        url = "https://api.sendinblue.com/v3/contacts"

        payload = {
            "attributes": {"FIRSTNAME": name},
            "listIds": [3],
            "updateEnabled": False,
            "email": email,
        }

        response = requests.request("POST", url, json=payload, headers=self.headers)

        print(response.text)
        pass


class SqsHandler(SendinblueHandler):
    def __init__(self, key):
        self.received_signal = False
        signal(SIGINT, self._signal_handler)
        signal(SIGTERM, self._signal_handler)
        self.key = key
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "api-key": self.key,
        }
        self.reply = {"email": "noreply@atdev.com", "name": "no-reply"}

    def _signal_handler(self, signal, frame):
        print(f"Handling signal {signal}, exiting gracefully")
        self.received_signal = True

    # {"name": name to show in email,"email": address to send email to , "isContact": boolean for only creating a contact via sendinblue}
    def process_message(
        self, sqs_message: str, email_template: str, email_subject: str
    ) -> None:
        print(
            f"Processing message: {sqs_message} with template {email_subject}: {email_template}"
        )
        message = json.loads(sqs_message)
        if message["isContact"]:
            self.make_sendinblue_message(
                message["email"], message["name"], email_template, email_subject
            )
        else:
            self.make_sendinblue_contact(
                message["email"], message["name"]
            )
        pass


def wait(seconds: int):
    def decorator(fun):
        last_run = time.monotonic()

        def new_fun(*args, **kwargs):
            nonlocal last_run
            now = time.monotonic()
            if time.monotonic() - last_run > seconds:
                last_run = now
                return fun(*args, **kwargs)

        return new_fun

    return decorator


@wait(seconds=60)
def send_queue_metrics(sqs_queue) -> None:
    print("Reading queue metrics")
    statsd.gauge(
        "sqs.queue.message_count",
        queue_length(sqs_queue),
        tags=[f"queue:{queue_name(sqs_queue)}"],
    )


def queue_length(sqs_queue) -> int:
    sqs_queue.load()
    return int(sqs_queue.attributes["ApproximateNumberOfMessages"])


def queue_name(sqs_queue) -> str:
    sqs_queue.load()
    return sqs_queue.attributes["QueueArn"].split(":")[-1]
