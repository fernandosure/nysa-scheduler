import rollbar
import sys
import boto3
from message_handlers import MessageScheduler
from secret_manager import get_secret
sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName=get_secret('NYSA_SCHEDULER_SQS_QUEUE'))
rollbar.init(get_secret('ROLLBAR_KEY'))


while 1:
    try:
        messages = queue.receive_messages(WaitTimeSeconds=20)
        for message in messages:
            MessageScheduler(message).execute()

    except:
        rollbar.report_exc_info(sys.exc_info())
