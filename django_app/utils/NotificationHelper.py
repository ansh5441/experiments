import logging
import threading
from datetime import timedelta

import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from django.utils.timezone import now

logger = logging.getLogger(__name__)


class NotificationHelper:
    def __init__(self):
        boto3.setup_default_session(region_name='us-east-1')
        self.client = boto3.client('sns', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                   aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

    def get_device_arn(self, token, device_type):
        """
        :param user: the users model
        :param token: Device token
        :param device_type: Device type (android or ios)
        :return: Standard json reply
        """
        if len(token) < 10:
            return False, 'Invalid device token'

        if device_type == 'ios':
            app = settings.APNS_IOS_APP_ARN
        elif device_type == 'android':
            app = settings.GCM_APP_ARN
        else:
            return False, 'invalid device type'
        try:
            response = self.client.create_platform_endpoint(
                PlatformApplicationArn=app,
                Token=token,
            )
        except ClientError as e:
            logger.error(str(e))
            return False, 'problem saving device'
        new_device_arn = response.get('EndpointArn')
        return new_device_arn

    def notify_receiver_again(self, device_arn, post_id):
        """
        :param device_arn: Amazon resource number for device
        :param sender_name: Name of the hifi sender
        :param sender_image: profile picture of the sender
        :param message: message of the hifi
        :param post_id: id of the hifi
        :param title: = Hifi
        :return: Response from amazon
        """
        if device_arn is None:
            return False
        message = r'''{
                "GCM":"{\"aps\":{\"content-available\":\"1\"},\"post\":\"post_id\"}",
                "APNS_SANDBOX":"{\"aps\":{\"content-available\":\"1\"},\"post\":\"post_id\"}",
                "APNS":"{\"aps\":{\"content-available\":\"1\"},\"post\":\"post_id\"}"
            }'''.replace(
            'post_id', str(post_id))
        return self._send_to_user(message, device_arn)

    def notify_sender(self, receiver_name, receiver_image, device_arn, title='Hyde', **kwargs):
        """
        :param receiver_name: Name of the receiver
        :param receiver_image: Profile picture of the receiver
        :param title: title for the notification
        :return: response from amazon
        """
        post_message = kwargs.get('post_message', '')
        message = r'''{
            "GCM": "{\"data\":{\"message\":\"msg\",\"title\":\"title_text\",\"image\":\"img\"}}",
            "APNS": "{\"aps\":{\"alert\": \"msg\", \"sound\":\"Glass.mp3\"} }"
        }'''.replace(
            'msg', receiver_name + " received your Hyde: '" + post_message + "'").replace(
            'title_text', title).replace(
            'img', settings.FILES_PREFIX + '/' + receiver_image)

        return self._send_to_user(message, device_arn)

    def notify_receiver(self, device_arn, sender_name, sender_image, message, post_id=0, title='Hyde'):
        """
        :param device_arn: Amazon resource number for device
        :param sender_name: Name of the hifi sender
        :param sender_image: profile picture of the sender
        :param message: message of the hifi
        :param post_id: id of the hifi
        :param title: = Hifi
        :return: Response from amazon
        """
        if device_arn is None:
            return False
        message = r'''{
            "GCM": "{\"data\":{\"message\":\"message_text\",\"image\":\"image_text\",\"title\":\"title_text\",\"post\":\"post_id\"}}",
            "APNS": "{\"aps\":{\"alert\": \"message_text\", \"sound\":\"Glass.mp3\"}, \"post\":\"post_id\" }"
        }'''.replace(
            'message_text', sender_name + ": " + message).replace(
            'image_text', settings.FILES_PREFIX + '/' + sender_image).replace(
            'title_text', title).replace(
            'post_id', str(post_id))

        return self._send_to_user(message, device_arn)

    def send_like_push(self, **kwargs):
        """
        :param device_arn: Amazon resource number for device
        :param sender_name: Name of the hifi sender
        :param sender_image: profile picture of the sender
        :param post_id: id of the hifi
        :return: Response from amazon
        """
        device_arn = kwargs.get('device_arn', None)
        receiver_name = kwargs.get('receiver_name', None)
        sender_image = kwargs.get('sender_image', None)
        post_id = kwargs.get('post_id', None)
        post_message = kwargs.get('post_message', None)

        if device_arn is None:
            return False
        message = r'''{
                    "GCM": "{\"data\":{\"message\":\"message_text\",\"image\":\"image_text\",\"title\":\"title_text\",\"post_liked\":\"post_id\"}}",
                    "APNS": "{\"aps\":{\"alert\": \"message_text\", \"sound\":\"Glass.mp3\"},\"post_liked\":\"post_id\"}"
                }'''.replace(
            'message_text', receiver_name + " liked your Hyde: '" + post_message + "'").replace(
            'image_text', settings.FILES_PREFIX + '/' + sender_image).replace(
            'title_text', "Hyde").replace(
            'post_id', str(post_id))
        return self._send_to_user(message, device_arn)

    def chat_push(self, device_arn, sender_name, sender_image, message):
        """
        :param device_arn: Amazon resource number for device
        :param sender_name: Name of the hifi sender
        :param sender_image: profile picture of the sender
        :param message: message of the hifi
        :return: Response from amazon
        """
        if device_arn is None:
            return False
        message = r'''{
            "GCM": "{\"data\":{\"message\":\"message_text\",\"image\":\"image_text\"}}",
            "APNS": "{\"aps\":{\"alert\": \"message_text\", \"sound\":\"Glass.mp3\"} }"
        }'''.replace(
            'message_text', sender_name + ": " + message).replace(
            'image_text', settings.FILES_PREFIX + '/' + sender_image)

        return self._send_to_user(message, device_arn)

    def silent_location_push(self, device_arn):
        if device_arn is None or type(device_arn) != str:
            return
        message = r'''{
                        "GCM": "{\"data\":{\"type\":\"silent\"}}",
                        "APNS": "{\"aps\":{\"content-available\":\"1\"}}"
                    }'''
        return self._send_to_user(message, device_arn)

    def silent_activity_push(self, device_arn):
        if device_arn is None or type(device_arn) != str:
            return
        message = r'''{
                    "GCM": "{\"data\":{\"type\":\"silent\",\"message\":\"activity\"}}",
                    "APNS": "{\"aps\":{\"content-available\":\"1\"},\"message\":\"activity\"}"
                }'''
        return self._send_to_user(message, device_arn)

    def silent_token_mismatch_push(self, token, device_type):
        if token is None or device_type is None or type(token) != str:
            return
        device_arn = self.get_device_arn(token, device_type)
        message = r'''{
                    "GCM": "{\"data\":{\"type\":\"silent\",\"message\":\"token_mismatch\"}}",
                    "APNS": "{\"aps\":{\"content-available\":\"1\"},\"message\":\"token_mismatch\"}"
                }'''
        return self._send_to_user(message, device_arn)

    def _subscribe_users_to_topic(self, to_sub, topic_arn=settings.LOCATION_TOPIC_ARN):
        for u in to_sub:
            response = self.client.subscribe(
                TopicArn=topic_arn,
                Protocol='application',
                Endpoint=u.device_arn
            )
            u.location_sub = response.get('SubscriptionArn')
            u.save()
        return True

    def _send_to_user(self, message, device_arn):
        logger.debug("Message = \n" + message)
        logger.debug("Device ARN = \n" + device_arn)
        try:
            response = self.client.publish(
                TargetArn=device_arn,
                Message=message,
                MessageStructure='json'
            )
            logger.info(response)
        except Exception as e:
            err = e.with_traceback(None)
            logger.error(err)
            response = False, 'EndpointDisabled' if 'EndpointDisabled' in str(err) else ""
        return response

    def _send_to_topic(self, message, topic_arn=settings.LOCATION_TOPIC_ARN):
        logger.info(message)
        try:
            response = self.client.publish(
                TopicArn=topic_arn,
                Message=message,
                MessageStructure='json'
            )

            logger.info(response)
        except Exception as e:
            logger.error(e.with_traceback(None))
            response = False
        return response


class AsyncNotification(threading.Thread):
    def __init__(self, **kwargs):
        threading.Thread.__init__(self)
        self.nh = NotificationHelper()
        self._kwargs = kwargs

    def run(self):
        command = self._kwargs.get('command', None)
        if command is None:
            return
        if command == 'silent_activity_push':
            resp = self.nh.silent_activity_push(self._kwargs.get('device_arn'))
            if type(resp) == tuple:
                if self._kwargs.get('user', None) is not None and 'EndpointDisabled' in resp[1]:
                    self._kwargs.get('user').delete_device_arn()
        elif command == 'silent_location_push':
            self.nh.silent_location_push(self._kwargs.get('device_arn'))
