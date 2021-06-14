import boto3
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

print(config.sections())
AWSID = config["aws"]["AWSID"]
AWSSEC = config["aws"]["AWSSEC"]
REGION = config["aws"]["REGION"]
SQS_QUEUE_NAME = config["aws"]["SQS_QUEUE_NAME"]
SQS_DEAD_LETTER_QUEUE_NAME = config["aws"]["SQS_DEAD_LETTER_QUEUE_NAME"]
EMAIL_TEMPLATE_OUT = config["email"]["HTML"]
EMAIL_SUBJECT = config["email"]["SUBJECT"]
SENDIN_BLUE_KEY = config["email"]["APIKEY"]

sqs = boto3.resource("sqs", aws_access_key_id = AWSID,
    aws_secret_access_key = AWSSEC,
    region_name = REGION)
queue = sqs.get_queue_by_name(QueueName=SQS_QUEUE_NAME)

# Create a new message
response = queue.send_message(MessageBody=EMAIL_TEMPLATE_OUT)

# The response is NOT a resource, but gives you a message ID and MD5
print(f'Uploaded a message with the id:{response.get("MessageId")}')