import boto3

from handler import Handler, process_message, send_queue_metrics

AWSID = "aws_secret_id"
AWSSEC = "aws_secret_secret"
REGION = "region"
SQS_QUEUE_NAME = "queue-name"
SQS_DEAD_LETTER_QUEUE_NAME = "queue-dead-letters"

sqs = boto3.resource("sqs", aws_access_key_id = AWSID,
    aws_secret_access_key = AWSSEC,
    region_name = REGION)
queue = sqs.get_queue_by_name(QueueName=SQS_QUEUE_NAME)
dlq = sqs.get_queue_by_name(QueueName=SQS_DEAD_LETTER_QUEUE_NAME)

if __name__ == "__main__":
    signal_handler = Handler()
    while not signal_handler.received_signal:
        send_queue_metrics(queue)
        send_queue_metrics(dlq)
        messages = queue.receive_messages(MaxNumberOfMessages=10, WaitTimeSeconds=1,)
        for message in messages:
            try:
                process_message(message.body)
            except Exception as e:
                print(f"exception while processing message: {repr(e)}")
                continue

            message.delete()