from __future__ import absolute_import

import logging
from datetime import timedelta

import boto3
import requests
from celery import shared_task
from django.conf import settings
from django.utils.timezone import now

from hf.models import Users
from hifi_api.celery import app
from utils.utils import RegisterCommand

logger = logging.getLogger(__name__)


@app.task
def test_task():
    f = open('task_test.txt', 'a')
    f.write(str(now) + ' cahl raha hai' '\n')
    f.close()


@shared_task
def location_notification():
    boto3.setup_default_session(region_name='us-east-1')
    client = boto3.client('sns', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

    # 1. Get all users from db whose location hasn't been updated in last 5 seconds and who are not flagged as logged
    #  out and are not subscribed. Subscribe them to topic if not subscribed, update subscription status
    time_threshold = now() - timedelta(seconds=5)
    excluded_status = [Users.FLAG_LOGGED_OUT]

    to_sub = Users.objects.filter(location__updated_at__lt=time_threshold).exclude(status__in=excluded_status).filter(
        location_sub=0).exclude(device_arn__isnull=True)
    for u in to_sub:
        response = client.subscribe(
            TopicArn=settings.LOCATION_TOPIC_ARN,
            Protocol='application',
            Endpoint=u.device_arn
        )
        u.location_sub = response.get('SubscriptionArn')
        u.save()

    to_sub = Users.objects.filter(location__updated_at__gt=time_threshold).exclude(
        status__in=excluded_status).exclude(location_sub=0).exclude(
        device_arn__isnull=True)
    for u in to_sub:
        response = client.unsubscribe(
            SubscriptionArn=u.location_sub,
        )
        logger.info(response)

    to_sub.update(location_sub=0)
    # 3. send notification to all users in the topic
    message = r'''{
                    "default": "\"content-available\": \"1\"",
                    "GCM": "{\"data\":{\"type\":\"silent\"}}",
                    "APNS": "{ \"aps\" : { \"content-available\": \"1\"} }",
                    "APNS_VOIP": "{ \"aps\" : { \"content-available\": \"1\"} }",
                    "APNS_SANDBOX": "{ \"aps\" : { \"content-available\": \"1\"} }"
                }'''

    response = client.publish(
        TopicArn=settings.LOCATION_TOPIC_ARN,
        Message=message,
        MessageStructure='json'
    )
    logger.info(response)
    return


@shared_task
def register_user_for_chat_async(**kwargs):
    xmp = RegisterCommand('admin@convers.im', 'Hifi1234', 'add-user', kwargs.get('digits_id') + "@convers.im",
                          kwargs.get('digits_id'))
    xmp.register_plugin('xep_0133')
    if xmp.connect(('convers.im', 5222), reattempt=True, use_tls=False):
        xmp.process(block=True)
        return True
    else:
        return False
