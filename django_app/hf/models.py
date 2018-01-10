import json
import logging
import random
from datetime import datetime, timedelta, time as dttime
import math
from pprint import pprint

import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.gis.db import models as mods
from django.contrib.gis.geos import Polygon, LineString
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Q
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.core import serializers
from pytz import timezone, utc
from hf.tagger import Tagger

from utils.ChatHelper import AsyncChatCommands, register_user_for_chat, set_user_status
from utils.NotificationHelper import NotificationHelper, AsyncNotification
from utils.utils import get_file_name, get_unique_token, get_day_num, make_thumbnail, find_timezone, get_thumb_bytes

logger = logging.getLogger(__name__)


def reply(status=False, msg="Some error occurred", code=500, dictionary=None):
    if dictionary is None:
        dictionary = {}
    ret = {'status': status, 'message': msg, 'code': code, 'data': dictionary}
    return JsonResponse(ret, status=code)


class Users(models.Model):
    FLAG_EMAIL_UNVERIFIED = 0
    FLAG_EMAIL_VERIFIED = 1
    FLAG_ACTIVE = 0
    FLAG_BACKGROUND = 1
    FLAG_TERMINATED = 2
    FLAG_LOGGED_OUT = 3
    LOCATION_SUB_NOT_SUBSCRIBED = 0
    LOCATION_SUB_SUBSCRIBED = 1
    fullname = models.CharField(max_length=255, null=True)
    userid = models.CharField(max_length=64, null=True, db_index=True)  # hf user ids
    avatar = models.FileField(null=True, upload_to='profile_pics')
    phone = models.CharField(max_length=15, null=True)
    digitsid = models.CharField(max_length=64, unique=True, default=None, db_index=True)
    email = models.CharField(max_length=256, default=None, null=True)
    version = models.IntegerField(default=0)
    device_token = models.CharField(max_length=256, null=True)
    device_arn = models.CharField(max_length=128, null=True)
    device_type = models.CharField(max_length=10, null=True, default=None)
    email_verified = models.CharField(max_length=40, null=True)
    status = models.CharField(max_length=1, null=True, default=None)
    location_sub = models.CharField(max_length=128, null=True, default=0)
    updated_at = models.DateTimeField(auto_now=True, null=True, db_index=True)
    created_at = models.DateTimeField(null=True)

    def register_device(self, token, device_type):
        """
        :param token: Device token
        :param device_type: Device type (android or ios)
        :return: Standard json reply
        """
        self.device_type = device_type
        self.device_token = token
        response = NotificationHelper().get_device_arn(token, device_type)
        if type(response) == tuple:
            return reply(response[0], response[1])

        self.device_arn = response
        self.save()
        return reply(True, 'user device saved')

    def delete_device_arn(self):
        self.device_arn = None
        self.save()

    def get_profile_dict(self):
        """
        :return: Get user profile dictionary
        """
        # data = serializers.serialize("json", [self])
        # return json.loads(data)[0]['fields']
        avt = ''
        if self.avatar.name != '' and self.avatar.name is not None:
            avt = settings.FILES_PREFIX + '/' + str(self.avatar.name)
        ret = {'name': self.fullname, 'phone': self.phone, 'userid': self.userid, 'avatar': avt,
               'digits_id': self.digitsid, 'version': self.version, 'email': self.email,
               'email_verified': True if self.email_verified == '0' and self.email is not None else False}
        return ret

    def __str__(self):
        dic = self.get_profile_dict()
        return ', '.join([str(k) + ": " + str(dic[k]) for k in dic.keys()]) + "\n\n"

    @staticmethod
    def get_by_id(uid):
        """
        :param uid: primary id of the user
        :return: user object
        """
        try:
            u = Users.objects.get(pk=uid)
        except ObjectDoesNotExist:
            u = None
        return u

    @staticmethod
    def get_by_digits_id(d_id):
        """
        :param d_id: digits id of the user
        :return: user object
        """
        try:
            u = Users.objects.get(digitsid=d_id)
        except ObjectDoesNotExist:
            u = None
        return u

    @staticmethod
    def get_by_hf_id(hf_id):
        """
        :param hf_id: hf id of the user
        :return: user object
        """
        try:
            u = Users.objects.get(userid=hf_id)
        except ObjectDoesNotExist:
            u = None
        return u

    def update_profile(self, name, phone, email, img, dev_token, dev_type, new_digits_id, remove_image):
        """
        :param name: New name of the user
        :param phone: New phone number of the user
        :param email: New email of the user
        :param img: New avatar of the user
        :param dev_token: New device token of the user
        :param dev_type: New device type of the user
        :param new_digits_id: New digits id of the user
        :param remove_image: If the profile image needs to be removed
        :return: Array of updated keys
        """
        updated = []
        if name is not None and name != self.fullname:
            updated.append('name')
            self.fullname = name
            background2 = AsyncChatCommands(name=name, digits_id=self.digitsid, command='set_user_vcard')
            background2.start()
            background = AsyncChatCommands(nick=name, digits_id=self.digitsid, command='change_user_nick')
            background.start()

        if phone is not None and phone != self.phone and new_digits_id is not None and new_digits_id != self.digitsid:
            updated.append('phone, digits id')
            self.phone = phone
            self.digitsid = new_digits_id

        if email is not None:
            updated.append('email')
            self.email = email
            token = get_unique_token()
            self.email_verified = token
            self.send_verification_email(token)
        thumb = None
        if img is not None and img.size > 0:
            updated.append('image')
            # img.name = get_file_name(img)
            img.name = str(self.digitsid) + '.jpg'
            self.avatar.delete()
            self.avatar = img
            thumb = get_thumb_bytes(img)
            background = AsyncChatCommands(image=thumb, digits_id=self.digitsid, command='set_user_vcard')
            background.start()

        if remove_image == 1:
            updated.append('image')
            self.avatar.delete()
            self.avatar = None
            background = AsyncChatCommands(name=self.fullname, image='', digits_id=self.digitsid,
                                           command='set_user_vcard')
            background.start()

        if dev_token is not None and dev_token != self.device_token:
            resp = json.loads(self.register_device(dev_token, dev_type).getvalue().decode())
            if resp.get('status') is True:
                updated.append('device token')

        if len(updated) > 0:
            self.version = int(self.version)
            self.version += 1
            self.updated_at = now()
            self.save()

        # set_user_vcard(name=name, image=thumb, digits_id=self.digitsid)
        return updated

    def create_user(self, d_id, name, phone, email, dev_token, dev_type, img):
        """
        :param d_id: Digits id of the user
        :param name: Name of the user
        :param phone: phone number of the user
        :param email: email id of the user
        :param dev_token: device token of the user
        :param dev_type: device type of the user
        :param img: profile picture of the user
        :return: user dictionary
        """
        us = Users()
        us.fullname = name
        us.phone = phone
        us.email = email
        us.digitsid = d_id
        thumb = None
        if img is not None and img.size > 0:
            # img.name = get_file_name(img)
            img.name = str(d_id) + '.jpg'
            us.avatar = img
            thumb = get_thumb_bytes(img)

        us.version = 0
        us.email_verified = get_unique_token()
        us.status = self.FLAG_ACTIVE
        us.created_at = now()
        us.updated_at = now()
        try:
            p = Users.objects.latest('id').id
        except ObjectDoesNotExist:
            p = 0
        us.userid = 'HF' + str(1 + p)
        us.save()
        if dev_token is not None:
            us.register_device(dev_token, dev_type)

        default_interest = Interest.objects.get(pk=2)
        UserInterest.subscribe_user(us, default_interest, 1)
        us.send_verification_email(us.email_verified)
        us.create_default_hifi(us)
        register_user_for_chat(digits_id=str(d_id))
        # image_url = settings.FILES_PREFIX + '/' + str(
        #     us.avatar.name) if us.avatar.name != '' and us.avatar.name is not None else None

        background = AsyncChatCommands(name=name, image=thumb, digits_id=d_id,
                                       command='set_user_vcard')
        background.start()

        # set_user_vcard(name=name, digits_id=d_id, image=thumb)
        resp = us.get_profile_dict()

        return resp

    def verified_email_exists(self, email):
        if email is None:
            return False
        em = Users.objects.filter(email=email, email_verified=0).count()
        return False if em < 1 else True

    def create_default_hifi(self, user):
        query = "SELECT i.id FROM `hf_interestdata` AS i JOIN hf_interest AS inter ON i.interest_id = inter.id WHERE inter.id = 2"

        interests = InterestData.objects.raw(query)
        tim = now()
        for inter in interests:
            try:
                post = Hifipost.objects.get(interest=inter)
            except ObjectDoesNotExist:
                post = Hifipost()
                post.interest = inter
                post.tag = inter.name
                post.post = inter.message
                post.lat = inter.lat
                post.lng = inter.lng
                post.attachment = inter.image
                post.post_coord = 'POINT( ' + str(post.lat) + ' ' + str(post.lng) + ')'
                post.location = inter.name
                post.repeat = '0'
                post.expiry = None
                post.updated_at = tim
                post.created_at = tim
                post.flag = Hifipost.FLAG_CREATED
                post.hf_userid = user.userid
                post.save()

            uh = Hifireceived()
            uh.post = post
            uh.postid = post.id
            uh.flag = Hifireceived.FLAG_RECEIVED
            uh.created_at = tim
            uh.updated_at = tim
            try:
                uh.receiver = user
                uh.hf_userid = user.userid
                uh.save()
            except ObjectDoesNotExist as e:
                logger.debug(e.with_traceback(None))

    def send_verification_email(self, token):

        msg_plain = render_to_string(settings.BASE_DIR + '/hf/templates/verification.txt',
                                     {'username': self.fullname, 'token': self.email_verified,
                                      'url': settings.BASE_URL})
        msg_html = render_to_string(settings.BASE_DIR + '/hf/templates/verification.html',
                                    {'username': self.fullname, 'token': token, 'url': settings.BASE_URL})
        try:
            send_mail(subject='Verify email for Hyde', message=msg_plain, from_email='Hyde <noreply@hifi.re>',
                      recipient_list=[self.email], html_message=msg_html)
        except Exception as e:
            logger.debug(e.with_traceback(None))


class Interest(models.Model):
    NOTIFICATION_TYPE_NOTIFICATION = 0
    NOTIFICATION_TYPE_POST = 1
    name = models.CharField(max_length=128)
    image = models.FileField(null=True, upload_to='interest')
    typ = models.CharField(max_length=64)
    description = models.CharField(max_length=512)
    notification_type = models.CharField(max_length=2, default=0)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(null=True)

    def __str__(self):
        return self.name

    def add_new(self, name):
        self.name = name
        self.created_at = now()
        self.updated_at = now()
        self.save()

    def get_dictionary(self):
        img = ''
        if self.image.name != '' and self.image.name is not None:
            img = settings.FILES_PREFIX + '/' + str(self.image.name)

        dictionary = {
            'id': self.id,
            'name': self.name,
            'avatar': img,
            'type': self.typ,
            'description': self.description
        }
        return dictionary

    @staticmethod
    def get_by_id(int_id):
        try:
            interest = Interest.objects.get(id=int_id)
        except ObjectDoesNotExist:
            interest = None
        return interest


class UserInterest(models.Model):
    STATUS_SUBSCRIBED = 1
    STATUS_NOT_SUBSCRIBED = 0
    user = models.ForeignKey(Users)
    sub = models.ForeignKey(Interest)
    status = models.CharField(max_length=1, default=1)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(null=True)

    def get_dictionary(self):
        dictionary = {
            'interest': self.sub.get_dictionary(),
            'status': self.status,
        }
        return dictionary

    def get_user_subscription(self, u):
        ints = Interest.objects.all()
        user_ints = UserInterest.objects.filter(user=u).filter(status=UserInterest.STATUS_SUBSCRIBED)
        user_ints_dict = {}
        for usi in user_ints:
            user_ints_dict[usi.sub.id] = usi

        ret = []
        for i in ints:
            dictionary = i.get_dictionary()
            sub = user_ints_dict.get(i.id, None)
            if sub is not None:
                dictionary['subscribed'] = True
            else:
                dictionary['subscribed'] = False
            ret.append(dictionary)
        return ret

    @staticmethod
    def subscribe_user(user, interest, status):
        try:
            user_interest = UserInterest.objects.get(user=user, sub=interest)
        except ObjectDoesNotExist:
            user_interest = UserInterest()
            user_interest.user = user
            user_interest.sub = interest
            tim = now()
            user_interest.created_at = tim
            user_interest.updated_at = tim

        user_interest.status = status
        user_interest.save()
        return True


class InterestData(models.Model):
    interest = models.ForeignKey(Interest)
    guid = models.CharField(max_length=64, unique=True, null=True)
    name = models.CharField(max_length=128)
    lat = models.FloatField()
    lng = models.FloatField()
    image = models.FileField(null=True, upload_to='interest_data', max_length=256)
    message = models.CharField(max_length=512, default='')
    distance = models.IntegerField(default=30)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(null=True)

    def get_dictionary(self):
        nam = self.interest.image.name
        if nam is not None and not nam.startswith('http'):
            nam = settings.FILES_PREFIX + '/' + nam
        dictionary = {
            'name': self.name,
            'lat': self.lat,
            'lng': self.lng,
            'avatar': nam,
            'message': self.message,
        }
        return dictionary

    def find_nearby_interests(self, lat, lng, uid, distance=settings.PROXIMITY):
        query = "SELECT ui.status, i.id, ( 6371000 * acos( cos( radians(%s) ) * cos( radians( lat ) ) * cos( radians( lng ) - radians(%s) ) + sin( radians(%s) ) * sin( radians( lat ) ) ) ) dist FROM `hf_interestdata` AS i JOIN hf_userinterest AS ui ON i.interest_id = ui.sub_id WHERE ui.user_id = %s AND ui.status = %s HAVING dist < %s ORDER BY dist LIMIT 100"

        interests = InterestData.objects.raw(query, [lat, lng, lat, uid, UserInterest.STATUS_SUBSCRIBED, distance])
        ret = []
        resp = {}
        for i in interests:
            key = i.interest.id
            if resp.get(key, None) is None:
                interest_image = ''
                if i.interest.image.name != '' and i.interest.image.name is not None:
                    interest_image = settings.FILES_PREFIX + '/' + str(i.interest.image.name)
                interest_dict = {
                    'id': i.interest.id,
                    'name': i.interest.name,
                    'image': interest_image,
                    'location': []
                }
                resp[key] = interest_dict
            resp[key]['location'].append(i.get_dictionary())
        for k in resp.keys():
            ret.append(resp[k])
        return ret


class Hifipost(models.Model):
    FLAG_CREATED = 0
    FLAG_DELETED = 1
    FLAG_COMPLETELY_DELETED = 2  # delete repetitions
    userid = models.CharField(max_length=64, default='')
    sender = models.ForeignKey(Users, null=True)  # Sender as django user
    interest = models.ForeignKey(InterestData, null=True)
    hf_userid = models.CharField(max_length=256, null=True)  # Array of users for hifi
    post = models.CharField(max_length=8192, null=True)  # Message
    location = models.CharField(max_length=256, null=True)  # Location as string
    lat = models.CharField(max_length=64, null=True)
    lng = models.CharField(max_length=64, null=True)
    post_coord = mods.PointField(geography=True, default=None)
    has_image = models.CharField(max_length=5, null=True)  # attachment filename extension
    attachment = models.FileField(null=True, upload_to='attachments')
    attachment_thumb = models.FileField(null=True, upload_to='attachments/thumb')
    map_image = models.FileField(null=True, upload_to='map_image')
    flag = models.IntegerField(null=True)
    repeat = models.CharField(max_length=20, null=True)
    expiry = models.DateTimeField(null=True)
    condition = models.IntegerField(null=True)
    tag = models.CharField(max_length=128, default='default')
    colour = models.CharField(max_length=6, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(null=True)

    def __str__(self):
        dic = self.get_detail_dict()
        return ', '.join([str(k) + ": " + str(dic[k]) for k in dic.keys()]) + "\n\n"

    def get_detail_dict(self):

        mim = ''
        if self.map_image.name != '' and self.map_image.name is not None:
            mim = settings.FILES_PREFIX + '/' + str(self.map_image.name)

        att = ''
        if self.attachment.name != '' and self.attachment.name is not None:
            att = settings.FILES_PREFIX + '/' + str(self.attachment.name)
        ret = {'post_id': self.id, 'post': self.post, 'lat': self.lat, 'lng': self.lng, 'to_users': self.hf_userid,
               'location': self.location, 'map_image': mim, 'attachment': att,
               'sender': self.sender.get_profile_dict() if self.sender is not None else "",
               'interest': self.interest.get_dictionary() if self.interest is not None else "",
               'tag_image': Tagger().get_image_from_tag(self.tag), 'created_at': self.created_at,
               'color': '#' + str(self.colour)}
        return ret

    def create_hifi(self, u, post, lat, lng, location, repeat, expiry, attachment, map_image, to_users, condition):
        h = Hifipost()
        h.sender = u
        h.userid = u.userid
        h.post = post
        h.lat = lat
        h.lng = lng
        h.location = location
        h.repeat = repeat
        h.expiry = expiry
        h.condition = condition
        h.post_coord = 'POINT( ' + lat + ' ' + lng + ')'

        # Assign color to hifi
        try:
            previous_colour = Hifipost.objects.filter(sender=u).latest('id').colour
        except:
            previous_colour = None
        colors_array = ['F44336', 'E91E63', '9C27B0', '673AB7', '3F51B5', '2196F3', '03A9F4', '00BCD4', '009688']
        new_colour = random.choice(colors_array)
        while previous_colour == new_colour:
            new_colour = random.choice(colors_array)
        h.colour = new_colour

        # add attachment
        if attachment is not None and attachment.size > 0:
            attachment.name = get_file_name(attachment)
            h.has_image = '1'
            h.attachment = attachment
            thumb = make_thumbnail(attachment, (500, 500))
            thumb.name = get_file_name(thumb)
            h.attachment_thumb = thumb

        if map_image is not None and map_image.size > 0:
            map_image.name = get_file_name(map_image)
            h.map_image = map_image

        tim = now()
        h.updated_at = tim
        h.created_at = tim
        h.flag = Hifipost.FLAG_CREATED
        h.hf_userid = to_users
        h.save()

        # create received entries
        to_users = to_users.split(',')
        for tu in to_users:
            uid = tu
            uh = Hifireceived()
            uh.post = h
            uh.postid = h.id
            uh.flag = Hifireceived.FLAG_NOT_RECEIVED
            uh.created_at = tim
            uh.updated_at = tim
            try:
                us = Users.get_by_hf_id(uid)
                uh.receiver = us
                uh.hf_userid = us.userid
                uh.save()
            except ObjectDoesNotExist as e:
                logger.debug(tu)
                logger.debug(e.with_traceback(None))

            # check if the user is nearby and send hifi immediately
            try:
                ul = Location.objects.get(user=us)
                if ul.updated_at > now() - timedelta(minutes=5):
                    ul.process_location_update(None)
            except ObjectDoesNotExist:
                pass
            # send a silent push to the user
            background = AsyncNotification(device_arn=us.device_arn, command='silent_location_push')
            background.start()

        # Send activity notification
        friends = Users.objects.filter(friend_from__to_user=u)

        for f in friends:
            background = AsyncNotification(device_arn=f.device_arn, command='silent_activity_push')
            background.start()

        return reply(True, 'Hyde created successfully', 200, h.get_detail_dict())

    def fetch_sent_hifi(self, u, page):
        hif = Hifipost.objects.filter(sender=u).filter(flag=Hifipost.FLAG_CREATED).order_by(
            '-created_at').select_related('sender')

        pag = Paginator(hif, 30)
        if page > pag.num_pages:
            return {'pages': pag.num_pages, 'hifis': {}}
        received_hifis = Hifireceived.objects.filter(post__in=pag.page(page)).select_related('receiver').select_related(
            'post').prefetch_related('post__sender')
        recs = {}
        for r in received_hifis:
            k = r.post.id
            if recs.get(k, None) is None:
                recs[k] = []
            avt = ''
            if r.receiver.avatar.name != '' and r.receiver.avatar.name is not None:
                avt = settings.FILES_PREFIX + '/' + str(r.receiver.avatar.name)

            dic = {
                'received': r.received_at if int(r.flag) == 1 else '',
                'avatar': avt,
                'like': r.like,
                'name': r.receiver.fullname,
                'version': r.receiver.version,
            }
            recs[k].append(dic)
        hifis = []
        for h in pag.page(page):
            h = h.get_detail_dict()
            h['receivers'] = recs[h['post_id']]
            hifis.append(h)
        return {'pages': pag.num_pages, 'hifis': hifis}


class Hifireceived(models.Model):
    FLAG_NOT_RECEIVED = 0
    FLAG_RECEIVED = 1
    FLAG_DELETED = 2
    REPORT_NOT_REPORTED = 0
    REPORT_REPORTED = 1
    NOT_LIKED = 0
    LIKED = 1
    UNLIKED = 2
    DELIVERED = 1
    NOT_DELIVERED = 0
    receiver = models.ForeignKey(Users)
    post = models.ForeignKey(Hifipost)
    hf_userid = models.CharField(max_length=64, default='')
    postid = models.CharField(max_length=64, default='')
    flag = models.CharField(max_length=1, null=True)
    like = models.CharField(max_length=1, null=True, default='0')
    report = models.CharField(max_length=1, null=True, default=REPORT_NOT_REPORTED)
    delivered = models.CharField(max_length=1, null=True, default='0', db_index=True)
    received_at = models.DateTimeField(null=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, db_index=True)
    created_at = models.DateTimeField(null=True)

    def get_detail_dict(self):
        ret = {'msg_id': self.id, 'hifi': self.post.get_detail_dict(), "flag": self.flag,
               'receiver_id': self.receiver.userid, 'created': self.created_at,
               'received': self.received_at, 'like': self.like}
        return ret

    def __str__(self):
        dic = self.get_detail_dict()
        return ', '.join([str(k) + ":" + str(dic[k]) for k in dic.keys()]) + "\n"

    def get_activity_feed(self, u, page):
        time_threshold = now() - timedelta(days=200)
        if time_threshold < u.created_at:
            time_threshold = u.created_at

        friends = Users.objects.filter(friend_from__to_user=u) | Users.objects.filter(id=u.id)
        friends = friends.distinct()
        hifi_recd = Hifireceived.objects.filter(Q(receiver__in=friends) | Q(post__sender__in=friends)).filter(
            created_at__gt=time_threshold).exclude(post__sender__isnull=True).order_by('-updated_at').select_related(
            'receiver').prefetch_related('post__sender')
        pag = Paginator(hifi_recd, 50)
        if page > pag.num_pages:
            return []
        hf = []
        posts_received = {}
        for h in pag.page(page):
            # add sent activity
            if h.post.sender in friends and h.post.id not in posts_received.keys():

                name = 'You' if h.post.sender == u else h.post.sender.fullname
                avatar = ''
                if h.post.sender.avatar.name != '' and h.post.sender.avatar.name is not None:
                    avatar = settings.FILES_PREFIX + '/' + str(h.post.sender.avatar.name)

                tim = h.created_at
                dic = {
                    'post_id': h.post.id,
                    'message': name + ' left a Hyde',
                    'avatar': avatar,
                    'type': 'sent',
                    'address': h.post.location,
                    'lat': h.post.lat,
                    'lng': h.post.lng,
                    'time': tim,
                    'tag_image': Tagger().get_image_from_tag(h.post.tag)
                }
                hf.append(dic)
                # save received status in posts dictionary
                if posts_received.get(h.post.id, None) is None:
                    posts_received[h.post.id] = []
                posts_received[h.post.id].append(h.flag)
            # add received activity
            if h.receiver in friends and str(h.flag) == str(Hifireceived.FLAG_RECEIVED) and h.receiver != u:
                name = h.receiver.fullname
                avatar = ''
                if h.receiver.avatar.name != '' and h.receiver.avatar.name is not None:
                    avatar = settings.FILES_PREFIX + '/' + str(h.receiver.avatar.name)

                tim = h.updated_at

                dic = {
                    'post_id': h.post.id,
                    'message': name + ' received a Hyde',
                    'avatar': avatar,
                    'type': 'received',
                    'address': h.post.location,
                    'lat': h.post.lat,
                    'lng': h.post.lng,
                    'time': tim,
                    'tag_image': Tagger().get_image_from_tag(h.post.tag)
                }
                hf.append(dic)

                # save received status in posts dictionary
                if posts_received.get(h.post.id, None) is None:
                    posts_received[h.post.id] = []
                posts_received[h.post.id].append(h.flag)

        # remove "you left a hifi" from hf if all hifis are received
        new_hf = []
        for h in hf:
            if h['type'] == 'sent':
                recd = True
                for r in posts_received.get(h['post_id'], []):
                    if r == '0':
                        recd = False
                        break
                if recd is False:
                    new_hf.append(h)
            else:
                new_hf.append(h)
        return {'activity': sorted(new_hf, key=lambda k: k['time'], reverse=True), 'pages': pag.num_pages}

    def fetch_received_hifis(self, u, page):

        blocked_users = Users.objects.filter(block_to__from_user=u, block_to__status='1')
        hifi = Hifireceived.objects.filter(receiver=u).filter(flag=Hifireceived.FLAG_RECEIVED).order_by(
            '-received_at').select_related('post').select_related('receiver').prefetch_related(
            'post__sender').prefetch_related('post__interest')
        pag = Paginator(hifi, 30)
        hf = []
        if page > pag.num_pages:
            return {}
        for h in pag.page(page):
            dictionary = h.get_detail_dict()
            if dictionary['hifi'].get('sender', '') != '':
                dictionary['hifi']['sender']['blocked'] = False
                if h.post.sender in blocked_users:
                    dictionary['hifi']['sender']['blocked'] = True
            hf.append(dictionary)
        return {'pages': pag.num_pages, 'hifis': hf}

    def notify_sender(self, posts):
        for p in posts:
            receiver = p.receiver
            sender = p.post.sender
            if sender != receiver and sender.device_arn is not None:
                try:
                    receiver_name = receiver.fullname

                    receiver_image = p.receiver.avatar.name
                    if receiver_image is not None or receiver_image == '':
                        receiver_image = settings.FILES_PREFIX + '/' + receiver_image
                    resp = NotificationHelper().notify_sender(receiver_name, receiver_image, p.post.sender.device_arn,
                                                              title='Hyde', post_message=p.post.post)
                    if type(resp) == tuple:
                        if 'EndpointDisabled' in resp[1]:
                            receiver.delete_device_arn()
                except Exception as e:
                    logger.error(e.with_traceback(None))

    def receive_hifis(self, posts, msg):
        # TODO refactor this
        count = 0
        posts2 = []
        for p in posts:
            if p.receiver.status == Users.FLAG_LOGGED_OUT:
                continue
            posts2.append(p)
            if count == 0:
                logger.info(str(posts.query) + "\n" + msg)
            logger.info(p)
            count += 1

            p.flag = Hifireceived.FLAG_RECEIVED
            p.delivered = 0 if p.post.condition == 1 or p.post.condition == '1' else 1
            # p.delivered = 0 if p.post.condition == 1 or p.post.condition == '1' else 1
            p.received_at = now()
            p.updated_at = now()
            p.save()

        # Looping again because multiple notifications would come with slow processing
        posts3 = []
        for p in posts2:
            if p.post.condition == 1:
                set_user_status(p.receiver.digitsid)
                continue
            receiver = p.receiver
            # Send receiver notification
            if receiver.device_arn is not None:
                try:
                    sender_name = p.post.sender.fullname
                    sender_image = p.post.sender.avatar.name
                    message = p.post.post
                    resp = NotificationHelper().notify_receiver(receiver.device_arn, sender_name, sender_image, message,
                                                                p.post.id)
                    if type(resp) == tuple:
                        if 'EndpointDisabled' in resp[1]:
                            receiver.delete_device_arn()

                except Exception as e:
                    logger.error(e.with_traceback(None))

            # Send activity notification
            friends = Users.objects.filter(friend_from__to_user=p.receiver)

            for f in friends:
                background = AsyncNotification(device_arn=f.device_arn, command='silent_activity_push', user=f)
                background.start()

            # Send hifi as chat
            sender = p.post.sender
            if sender != receiver:
                background2 = AsyncChatCommands(digits_id=sender.digitsid, from_user_did=sender.digitsid,
                                                to_user_did=receiver.digitsid, post=p.post.post,
                                                command='send_hifi_as_chat')
                background2.start()
            posts3.append(p)

        self.notify_sender(posts3)

    def get_post_details(self, post_id, user):
        blocked_users = Users.objects.filter(block_to__from_user=user, block_to__status='1')
        try:
            post = Hifireceived.objects.filter(receiver=user, post__id=post_id).select_related('post').prefetch_related(
                'post__sender')[0]
        except:
            return False, 'post not found'
        dictionary = post.get_detail_dict()
        if dictionary['hifi'].get('sender', '') != '':
            dictionary['hifi']['sender']['blocked'] = False
            if post.post.sender in blocked_users:
                dictionary['hifi']['sender']['blocked'] = True

        return dictionary

    def set_like_flag(self, post_id, u, like_flag):
        try:
            post = Hifireceived.objects.filter(receiver=u, post__id=post_id).select_related('post').prefetch_related(
                'post__sender')[0]
        except:
            return False, 'post not found'
        if like_flag == Hifireceived.NOT_LIKED:
            like_flag = Hifireceived.UNLIKED

        if like_flag == Hifireceived.LIKED and int(
                post.like) == Hifireceived.NOT_LIKED and post.receiver != post.post.sender:
            avt = ''
            if u.avatar.name != '' and u.avatar.name is not None:
                avt = settings.FILES_PREFIX + '/' + str(u.avatar.name)
            if post.post.sender is not None:
                resp = NotificationHelper().send_like_push(device_arn=post.post.sender.device_arn, sender_image=avt,
                                                           receiver_name=post.receiver.fullname, post_id=post.id,
                                                           post_message=post.post.post)
                if type(resp) == tuple:
                    if resp[1] == 'EndpointDisabled':
                        post.post.sender.delete_device_arn()
        post.like = like_flag
        post.save()
        return True


class Location(mods.Model):
    userid = mods.CharField(max_length=64, null=True)
    user = mods.ForeignKey(Users)
    loc_coord = mods.PointField(geography=True, default=None)
    lat = mods.CharField(max_length=64, null=True)
    lng = mods.CharField(max_length=64, null=True)
    average = models.FloatField(null=True, default=0)
    total = models.IntegerField(null=True, default=0)
    updated_at = mods.DateTimeField(auto_now=True, null=True)
    created_at = mods.DateTimeField(null=True)

    def process_location_update(self, old_coord):
        tz = find_timezone(self.lat, self.lng)
        try:
            tz = timezone(tz)
        except Exception as e:
            logger.error(e.with_traceback(None))
            tz = timezone('UTC')
        aware_datetime = tz.localize(datetime.combine(datetime.today(), dttime.min))

        self.when_they_reach_circle(aware_datetime)
        self.when_i_reach_circle(aware_datetime)
        if old_coord is not None and (old_coord['lat'] != float(self.lat) or old_coord['lng'] != float(self.lng)):
            if abs(float(old_coord['lat']) - float(self.lat)) < 0.006 and abs(
                            float(old_coord['lng']) - float(self.lng)) < 0.006:
                self.when_they_reach_box(old_coord, aware_datetime)
                self.when_i_reach_box(old_coord, aware_datetime)

    def get_bounding_polygon(self, old_coord, new_coord):
        try:
            theta = math.atan((old_coord['lat'] - new_coord['lat']) / (old_coord['lng'] - new_coord['lng']))
        except ZeroDivisionError:
            theta = 1.57079633 if old_coord['lat'] < new_coord['lat'] else 4.71238899
        delta_x = settings.PROXIMITY * math.sin(theta) / (111045 * math.cos(math.radians(new_coord['lat'])))
        delta_y = -settings.PROXIMITY * math.cos(theta) / 111045
        point_1 = old_coord['lng'] + delta_x, old_coord['lat'] + delta_y
        point_2 = old_coord['lng'] - delta_x, old_coord['lat'] - delta_y
        point_3 = new_coord['lng'] - delta_x, new_coord['lat'] - delta_y
        point_4 = new_coord['lng'] + delta_x, new_coord['lat'] + delta_y

        return Polygon((point_1, point_2, point_3, point_4, point_1))

    def when_i_reach_box(self, old_coord, date):

        polygon = self.get_bounding_polygon(old_coord, {'lat': float(self.lat), 'lng': float(self.lng)})
        flag_arr = [Hifireceived.FLAG_NOT_RECEIVED, Hifireceived.FLAG_RECEIVED]
        and_q = Q(post__repeat__contains=get_day_num(), post__expiry__gt=str(now()), flag__in=flag_arr,
                  received_at__lt=date)
        distance = 57.3 * settings.PROXIMITY / 6371000
        posts = Hifireceived.objects.filter(post__sender=self.user).filter(
            post__lat__range=(float(self.lat) - distance, float(self.lat) + distance)).filter(
            post__lng__range=(float(self.lng) - distance, float(self.lng) + distance)).filter(
            post__post_coord__within=polygon).filter(
            Q(flag=Hifireceived.FLAG_NOT_RECEIVED) | and_q).filter(post__condition=1)

        Hifireceived().receive_hifis(posts, 'When I reach box')

    def when_they_reach_box(self, old_coord, date):
        polygon = self.get_bounding_polygon(old_coord, {'lat': float(self.lat), 'lng': float(self.lng)})
        flag_arr = [Hifireceived.FLAG_NOT_RECEIVED, Hifireceived.FLAG_RECEIVED]
        and_q = Q(post__repeat__contains=get_day_num(), post__expiry__gt=str(now()), flag__in=flag_arr,
                  received_at__lt=date)
        distance = 57.3 * settings.PROXIMITY / 6371000
        posts = Hifireceived.objects.filter(receiver=self.user).filter(
            post__lat__range=(float(self.lat) - distance, float(self.lat) + distance)).filter(
            post__lng__range=(float(self.lng) - distance, float(self.lng) + distance)).filter(
            post__post_coord__contained=polygon).filter(
            Q(flag=Hifireceived.FLAG_NOT_RECEIVED) | and_q).filter(post__condition=0)

        Hifireceived().receive_hifis(posts, 'When they reach box')

    def when_they_reach_circle(self, date):
        distance = 57.3 * settings.PROXIMITY / 6371000
        query = "SELECT r.id, ( 6371000 * acos( cos( radians(%s) ) * cos( radians( lat ) ) * cos(radians ( lng ) - radians(%s) ) + sin( radians(%s) ) * sin( radians( lat ) ) ) ) dist FROM `hf_hifipost` AS p JOIN `hf_hifireceived` AS r ON p.id = r.post_id WHERE `condition` = 0 AND `receiver_id`= %s AND lat BETWEEN %s AND %s AND lng BETWEEN %s AND %s AND (r.flag=%s AND (p.repeat = 0 OR p.repeat LIKE %s) OR (p.repeat LIKE %s AND p.expiry >%s AND r.received_at < %s AND r.flag IN (0,1))) HAVING dist < '%s'"

        posts = Hifireceived.objects.raw(query,
                                         [self.lat, self.lng, self.lat, self.user.id, float(self.lat) - distance,
                                          float(self.lat) + distance, float(self.lng) - distance,
                                          float(self.lng) + distance, Hifireceived.FLAG_NOT_RECEIVED,
                                          '%' + str(get_day_num()) + '%', '%' + str(get_day_num()) + '%', now(), date,
                                          settings.PROXIMITY])
        Hifireceived().receive_hifis(posts, 'When they reach circle')

    def when_i_reach_circle(self, date):
        distance = 57.3 * settings.PROXIMITY / 6371000
        query = "SELECT r.id, ( 6371000 * acos( cos( radians(%s) ) * cos( radians( lat ) ) * cos(radians ( lng )  - radians(%s) ) + sin( radians(%s) ) * sin( radians( lat ) ) ) ) dist FROM `hf_hifipost` AS p JOIN `hf_hifireceived` AS r ON p.id = r.post_id WHERE `condition` = 1 AND `sender_id`= %s AND lat BETWEEN %s AND %s AND lng BETWEEN %s AND %s AND (r.flag=%s AND (p.repeat = 0 OR p.repeat LIKE %s) OR (p.repeat LIKE %s AND p.expiry > %s AND r.received_at < %s AND r.flag IN (0,1))) HAVING dist < '%s'"

        posts = Hifireceived.objects.raw(query,
                                         [self.lat, self.lng, self.lat, self.user.id, float(self.lat) - distance,
                                          float(self.lat) + distance, float(self.lng) - distance,
                                          float(self.lng) + distance, Hifireceived.FLAG_NOT_RECEIVED,
                                          '%' + str(get_day_num()) + '%', '%' + str(get_day_num()) + '%', now(), date,
                                          settings.PROXIMITY])
        Hifireceived().receive_hifis(posts, 'When I reach circle')

    def send_interest_notification(self):
        distance = 57.3 * settings.PROXIMITY / 6371000
        query = "SELECT ui.status, i.id, ( 6371000 * acos( cos( radians(%s) ) * cos( radians( lat ) ) * cos( radians( lng ) - radians(%s) ) + sin( radians(%s) ) * sin( radians( lat ) ) ) ) dist FROM `hf_interestdata` AS i JOIN hf_userinterest AS ui ON i.interest_id = ui.sub_id WHERE ui.user_id = %s AND lat BETWEEN %s AND %s AND lng BETWEEN %s AND %s AND ui.status = %s HAVING dist < %s LIMIT 100"

        interests = InterestData.objects.raw(query,
                                             [self.lat, self.lng, self.lat, self.user.id, float(self.lat) - distance,
                                              float(self.lat) + distance, float(self.lng) - distance,
                                              float(self.lng) + distance, UserInterest.STATUS_SUBSCRIBED,
                                              settings.PROXIMITY])
        tim = now()
        for inter in interests:
            try:
                notification = UserInterestNotification.objects.get(user=self.user, interest_data=inter)
            except ObjectDoesNotExist:
                notification = None
            except MultipleObjectsReturned:
                obs = UserInterestNotification.objects.filter(user=self.user, interest_data=inter)
                obs.delete()
                notification = None
            time_difference = tim - timedelta(hours=3)
            if notification is None or notification.created_at < time_difference:

                sender_name = inter.name
                sender_image = inter.interest.image.name
                message = inter.message
                title = inter.interest.name
                resp = NotificationHelper().notify_receiver(self.user.device_arn, sender_name, sender_image,
                                                            message, 0, title)
                if type(resp) == tuple:
                    if resp[1] == 'EndpointDisabled':
                        self.user.delete_device_arn()

                if notification is None:
                    notification = UserInterestNotification()
                    notification.user = self.user
                    notification.interest_data = inter
                notification.created_at = tim
                notification.save()

    def get_dictionary(self):
        return {
            'lat': self.lat,
            'lng': self.lat,
            'user': self.user.get_profile_dict()
        }

    def __str__(self):
        dic = self.get_dictionary()
        return ', '.join([str(k) + ": " + str(dic[k]) for k in dic.keys()]) + "\n\n"


class Friend(models.Model):
    FLAG_INACTIVE = 0
    FLAG_ACTIVE = 1
    from_user = models.ForeignKey(Users, related_name='friend_from')
    to_user = models.ForeignKey(Users, related_name='friend_to')
    status = models.CharField(max_length=2, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(null=True)

    def get_detail_dict(self):
        ret = {'from_user': self.from_user.get_profile_dict(), 'to_user': self.to_user.get_profile_dict(),
               "status": self.status}
        return ret

    def __str__(self):
        dic = self.get_detail_dict()
        return ', '.join([str(k) + ":" + str(dic[k]) for k in dic.keys()]) + "\n"

    def add_friends_by_contact(self, u, ph_nos):
        friends = Friend.objects.filter(from_user=u).select_related('to_user')
        prev_friends = []
        ret = []
        for f in friends:
            prev_friends.append(f.to_user)
            ret.append(f.to_user.get_profile_dict())

        ph_nos = ph_nos.split(',')
        ph_nos = list(set(ph_nos))
        if len(ph_nos) > 0:
            users = Users.objects.filter(phone__contains=str(ph_nos[0]))
        for p in ph_nos:
            if len(p) < 9 or p == ph_nos[0]:
                continue
            users = users | Users.objects.filter(phone__contains=str(p))

        for user in users:
            if user == u:
                continue
            if user in prev_friends:
                prev_friends.remove(user)
                continue
            fr = Friend()
            fr.from_user = u
            fr.to_user = user
            fr.created_at = now()
            fr.updated_at = now()
            fr.status = self.FLAG_ACTIVE
            fr.save()
            ret.append(user.get_profile_dict())

        for p in prev_friends:
            ret.remove(p.get_profile_dict())
            Friend.objects.filter(from_user=u, to_user=p).delete()

        chat_contacts = ret[:]
        to_friends = Friend.objects.filter(to_user=u).select_related('from_user')
        for t in to_friends:
            usex = t.from_user.get_profile_dict()
            if usex not in chat_contacts:
                chat_contacts.append(usex)

        digits_id_dict = {}
        for us in chat_contacts:
            digits_id_dict[us['digits_id']] = us['name']

        background = AsyncChatCommands(digits_id=u.digitsid,
                                       digits_id_dict=digits_id_dict,
                                       name=u.fullname,
                                       command='sync_roster')
        background.start()
        return ret


class Block(models.Model):
    from_user = models.ForeignKey(Users, related_name='block_from', null=True)
    to_user = models.ForeignKey(Users, related_name='block_to', null=True)
    userid = models.CharField(max_length=128, default='')
    block_userid = models.CharField(max_length=128, default='')
    status = models.CharField(max_length=1, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(null=True)

    def __str__(self):
        dic = self.get_detail_dict()
        return ', '.join([str(k) + ": " + str(dic[k]) for k in dic.keys()]) + "\n\n"

    def get_detail_dict(self):
        ret = {'id': self.id, 'from_user': self.from_user.get_profile_dict(),
               'hf_userid': self.to_user.get_profile_dict(), 'status': self.status}
        return ret


class UserInterestNotification(models.Model):
    user = models.ForeignKey(Users, null=True)
    interest_data = models.ForeignKey(InterestData, null=True)
    created_at = models.DateTimeField(null=True)
