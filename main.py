import boto3
import configparser

from handler import Handler, send_queue_metrics



config = configparser.ConfigParser()
config.read('config.ini')

print(config.sections())
AWSID = config["aws"]["AWSID"]
AWSSEC = config["aws"]["AWSSEC"]
REGION = config["aws"]["REGION"]
SQS_QUEUE_NAME = config["aws"]["SQS_QUEUE_NAME"]
SQS_DEAD_LETTER_QUEUE_NAME = config["aws"]["SQS_DEAD_LETTER_QUEUE_NAME"]
EMAIL_TEMPLATE = config["email"]["HTML"]
EMAIL_SUBJECT = config["email"]["SUBJECT"]
SENDIN_BLUE_KEY = config["email"]["APIKEY"]

sqs = boto3.resource("sqs", aws_access_key_id = AWSID,
    aws_secret_access_key = AWSSEC,
    region_name = REGION)
queue = sqs.get_queue_by_name(QueueName=SQS_QUEUE_NAME)
dlq = sqs.get_queue_by_name(QueueName=SQS_DEAD_LETTER_QUEUE_NAME)

if __name__ == "__main__":
    signal_handler = Handler(SENDIN_BLUE_KEY)
    while not signal_handler.received_signal:
        send_queue_metrics(queue)
        send_queue_metrics(dlq)
        messages = queue.receive_messages(MaxNumberOfMessages=10, WaitTimeSeconds=1,)
        for message in messages:
            try:
                signal_handler.process_message(message.body, EMAIL_TEMPLATE, EMAIL_SUBJECT)
            except Exception as e:
                print(f"exception while processing message: {repr(e)}")
                continue
            message.delete()