import boto3
import json
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

print(config.sections())
AWSID = config["aws"]["AWSID"]
AWSSEC = config["aws"]["AWSSEC"]
REGION = config["aws"]["REGION"]
SQS_QUEUE_NAME = config["aws"]["SQS_QUEUE_NAME"]
SQS_DEAD_LETTER_QUEUE_NAME = config["aws"]["SQS_DEAD_LETTER_QUEUE_NAME"]
SENDIN_BLUE_KEY = config["email"]["APIKEY"]

class SqsProducer():
    def __init__(self, AWSID:str, AWSSEC:str, REGION:str, SQS_QUEUE_NAME:str):
        sqs = boto3.resource("sqs", aws_access_key_id = AWSID,
            aws_secret_access_key = AWSSEC,
            region_name = REGION)
        self.queue = sqs.get_queue_by_name(QueueName=SQS_QUEUE_NAME)

    def new_message(self, message:dict)->None:
        # Create a new message
        response = self.queue.send_message(MessageBody=json.dumps(message))
        # The response is NOT a resource, but gives you a message ID and MD5
        print(f'Uploaded a message with the id:{response.get("MessageId")}')


if __name__ == "__main__":
    producer=SqsProducer(AWSID, AWSSEC, REGION, SQS_QUEUE_NAME)
    producer.new_message({"name": "Andrei","email": "tuta.andrei96@gmail.com" , "subject": "text to show as subject of the email","isContact": "False"})