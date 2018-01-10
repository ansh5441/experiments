import hashlib
import html
import logging
import random
from datetime import timedelta, datetime, time as dttime

import requests
from django.http import HttpResponse
from pytz import timezone

import boto3
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt

from hf.models import Location, Users, Hifipost, Hifireceived
from hf.views import reply
from utils.NotificationHelper import NotificationHelper, AsyncNotification
from utils.ChatHelper import ChatHelper, AsyncChatCommands
from utils.utils import desc
from .models import Tag, SubscriptionEmail, CampusAmbassador, Img, Typ
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)


@csrf_exempt
def edit_tags(request):
    tags = Tag.objects.all()
    dic = {}
    for t in tags:
        if dic.get(t.pic.pic.name, None) is None:
            dic[t.pic.pic.name] = []
        dic[t.pic.pic.name].append((t.get_dic()))
    for d in dic.items():
        print(d)
    data = [t.get_dic() for t in tags]
    return render(request, 'edit_tags.html', {'tags': data})


@csrf_exempt
def location_notification(request):
    boto3.setup_default_session(region_name='us-east-1')
    client = boto3.client('sns', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

    # 1. Get all users from db whose location hasn't been updated in last 30 seconds and who are not flagged as logged
    #  out and are not subscribed. Subscribe them to topic if not subscribed, update subscription status
    time_threshold = now() - timedelta(seconds=300)
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
    # 2. unsubscribe users who have a) updated location or b)are logged out or c) have no device arn
    to_unsub = Users.objects.filter(location__updated_at__gt=time_threshold) | Users.objects.filter(
        status__in=excluded_status) | Users.objects.filter(device_arn__isnull=True)
    to_unsub = to_unsub.exclude(location_sub=0)
    for u in to_unsub:
        response = client.unsubscribe(
            SubscriptionArn=u.location_sub,
        )
    to_unsub.update(location_sub=0)
    # 3. send notification to all users in the topic

    message = r'''{
                "default": "\"content-available\": \"1\"",
                "GCM": "{\"data\":{\"type\":\"silent\"}}",
                "APNS": "{ \"aps\" : { \"content-available\": \"1\"} }"
            }'''

    response = client.publish(
        TopicArn=settings.LOCATION_TOPIC_ARN,
        Message=message,
        MessageStructure='json'
    )
    logger.info(response)
    return reply(True, 'location notifications sent', 200)


@csrf_exempt
def location_notification_to_user(request):
    uid = request.POST.get('id', None)
    if uid is None:
        return reply(False, "Id not found", 400)
    u = Users.objects.get(id=uid)
    if u.device_arn is None:
        return reply(False, "User device arn is Null", 400)

    NotificationHelper().silent_location_push(u.device_arn)
    return reply(True, 'location notifications sent', 200)


@csrf_exempt
def save_subscription_email(request):
    em = find_key_in_request('email', request)
    if em is not False:
        try:
            sub = SubscriptionEmail.objects.get(email=em)
        except:
            sub = SubscriptionEmail()
            sub.email = em
            sub.created_at = now()
            sub.save()
        else:
            return reply(False, 'Already subscribed', 400)

        return reply(True, 'success', 200)


@csrf_exempt
def save_campus_ambassador(request):
    c = CampusAmbassador()
    c.first_name = find_key_in_request('first_name', request)
    c.last_name = find_key_in_request('last_name', request)
    c.email = find_key_in_request('email', request)
    c.university = find_key_in_request('university', request)
    c.major = find_key_in_request('major', request)
    c.phone = find_key_in_request('phone', request)
    c.fb = find_key_in_request('fb', request)
    c.country = find_key_in_request('country', request)
    c.how_popular = find_key_in_request('how_popular', request)
    c.referral = generate_referral(c.first_name)
    c.created_at = now()

    try:
        c.save()
    except Exception as e:
        logger.error(e.with_traceback(None))
        return reply(False, 'failure', 501)

    msg_plain = render_to_string(settings.BASE_DIR + '/utils/templates/utils/verification.txt',
                                 {'username': c.first_name, 'referral': c.referral})

    msg_html = render_to_string(settings.BASE_DIR + '/utils/templates/utils/verification.html',
                                {'name': c.first_name, 'referral': c.referral})
    try:
        send_mail('Welcome to Campus Ambassador program', msg_plain, 'noreply@storyboard.co', [c.email],
                  html_message=msg_html)
    except Exception as e:
        logger.debug(e.with_traceback(None))

    return reply(True, 'success', 200, {})


@csrf_exempt
def report(request):
    dictionary = {}
    dictionary['total_users'] = Users.objects.count()
    time_threshold = now() - timedelta(minutes=15)
    dictionary['current_active_users'] = Location.objects.filter(updated_at__gt=time_threshold).count()
    tz = timezone('UTC')
    today_threshold = tz.localize(datetime.combine(datetime.today(), dttime.min))
    dictionary['today_registered_users'] = Users.objects.filter(created_at__gt=today_threshold).count()
    dictionary['today_active_users'] = Location.objects.filter(updated_at__gt=today_threshold).count()
    dictionary['hifi_created'] = Hifipost.objects.filter(created_at__gt=today_threshold).count()
    dictionary['hifi_received'] = Hifireceived.objects.filter(updated_at__gt=today_threshold).count()
    return render(request, 'utils/report.html', dictionary)


@csrf_exempt
def ios_build(request):
    file_path = settings.BASE_DIR + "/ios_build.log"
    if request.method == 'POST':
        post = request.POST
        fa = open(file_path, 'a')
        st = ''
        st += '#' + post.get('heading', "") + '\n'
        st += post.get('message', "") + '\n'
        st += str(now()) + '\n'
        st += '---' + '\n'
        fa.write(st)
        fa.close()

    f = open(file_path, 'r')
    resp = []
    tup = {}
    for line in list(f):
        line = line.strip()
        if line == '---':
            if tup is not None:
                resp.append(tup)
            tup = {}
        elif line.startswith('#'):
            tup['heading'] = line[1:]
        else:
            if tup.get('message', None) is None:
                tup['message'] = [line]
            else:
                tup['message'].append(line)
    f.close()
    return render(request, 'utils/version.html', {'resp': reversed(resp)})


@csrf_exempt
def android_build(request):
    file_path = settings.BASE_DIR + "/android_build.log"
    if request.method == 'POST':
        post = request.POST
        fa = open(file_path, 'a')
        st = ''
        st += '#' + post.get('heading', "") + '\n'
        st += post.get('message', "") + '\n'
        st += str(now()) + '\n'
        st += '---' + '\n'
        fa.write(st)
        fa.close()

    f = open(file_path, 'r')
    resp = []
    tup = {}
    for line in list(f):
        line = line.strip()
        if line == '---':
            if tup is not None:
                resp.append(tup)
            tup = {}
        elif line.startswith('#'):
            tup['heading'] = line[1:]
        else:
            if tup.get('message', None) is None:
                tup['message'] = [line]
            else:
                tup['message'].append(line)
    f.close()
    return render(request, 'utils/version.html', {'resp': reversed(resp)})


@csrf_exempt
def send_undelivered_hifis(request):
    posts = Hifireceived.objects.filter(flag=Hifireceived.FLAG_RECEIVED).filter(
        delivered=Hifireceived.NOT_DELIVERED).filter(
        receiver__status__in=[Users.FLAG_ACTIVE, Users.FLAG_BACKGROUND]).filter(post__sender__isnull=False)

    posts2 = []
    tim = now()
    for p in posts:
        posts2.append(p)
        p.delivered = Hifireceived.DELIVERED
        p.received_at = tim
        p.updated_at = tim
        p.save()

    # Looping again because multiple notifications would come with slow processing
    posts3 = []
    for p in posts2:
        if p.post.condition == 0 or p.post.condition == '0':
            pass
        receiver = p.receiver
        # Send receiver notification
        if receiver.device_arn is not None:
            try:
                sender_name = p.post.sender.fullname
                sender_image = p.post.sender.avatar.name
                message = p.post.post
                resp = NotificationHelper().notify_receiver(receiver.device_arn, sender_name, sender_image,
                                                            message,
                                                            p.post.id)
                if type(resp) == tuple:
                    if 'EndpointDisabled' in resp[1]:
                        receiver.delete_device_arn()

            except Exception as e:
                logger.error(e.with_traceback(None))

        # Send activity notification
        friends = Users.objects.filter(friend_from__to_user=p.receiver)

        for f in friends:
            background = AsyncNotification(device_arn=f.device_arn, command='silent_activity_push')
            background.start()

        # Send hifi as chat
        sender = p.post.sender
        if sender != receiver:
            background2 = AsyncChatCommands(digits_id=sender.digitsid, from_user_did=sender.digitsid,
                                            to_user_did=receiver.digitsid, post=p.post.post,
                                            command='send_hifi_as_chat')
            background2.start()
        posts3.append(p)
    Hifireceived().notify_sender(posts3)
    return reply(True, 'pending messages delivered', 200)


#
# @csrf_exempt
# def temp_rename_user_avatar(request):
#     users = Users.objects.all()
#     for u in users:
#         if u.avatar.name is None or u.avatar.name == "":
#             continue
#         pic_url = settings.FILES_PREFIX + "/" + str(u.avatar.name)
#         try:
#             image = requests.get(pic_url).content
#         except:
#             image = None
#         post_request = {'digits_id': u.digitsid}
#         requests.post(settings.BASE_URL + '/update_user_profile/', post_request, files={'photo': image})
#
#     return reply(True, 'location notifications sent', 200)
#

def find_key_in_request(key, request):
    em = request.POST.get(key, None)
    if em is None:
        em = request.GET.get(key, None)
    return em


def get_file_name(fil):
    t = str(now())
    m = hashlib.md5(str.encode(t + str(random.randint(0, 9999999))))
    return "t" + t[5:10] + '_' + t[11:19] + "_" + m.hexdigest()[:16] + '.' + fil.name.split('.')[-1]


def generate_referral(key):
    if len(key) > 10:
        key = key[:random.randint(7, 10)]
    rand_length = 0
    existing = CampusAmbassador.objects.filter(referral__startswith=key).values('referral')
    ex = [e['referral'] for e in existing]
    while True:
        rnd = random.randint(10 ** rand_length, 10 ** (rand_length + 1))
        ref = key + str(rnd)
        if ref not in ex:
            return ref
        else:
            rand_length += 1
