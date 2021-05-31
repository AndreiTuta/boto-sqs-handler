# will extend https://github.com/Pastromhaug/code_samples/blob/master/sqs_consumer/sqs_consumer.py
import time
import requests
import json
from signal import SIGINT, SIGTERM, signal

from datadog import statsd

def make_sendinblue_message(email: str, name:str) -> None:

    url = "https://api.sendinblue.com/v3/smtp/email"

    payload = "request"

    response = requests.request("POST", url, json=payload, headers=headers)

    print(response.text)
    pass


def process_message(sqs_message: str) -> None:
    print(f"Processing message: {sqs_message}")
    message = json.loads(sqs_message)
    make_sendinblue_message(message["email"],message["name"])
    # process your sqs message here
    pass

class Handler:
    def __init__(self):
        self.received_signal = False
        signal(SIGINT, self._signal_handler)
        signal(SIGTERM, self._signal_handler)

    def _signal_handler(self, signal, frame):
        print(f"Handling signal {signal}, exiting gracefully")
        self.received_signal = True

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
    print("Sending queue metrics")
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