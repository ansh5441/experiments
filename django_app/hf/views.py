import logging
import os

from django.conf import settings
from django.contrib.auth import logout
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt

# from utils.utils import desc
from utils.NotificationHelper import NotificationHelper
from utils.utils import desc
from .models import Users, Hifipost, Location, Hifireceived, Block, Friend, UserInterest, InterestData, Interest

# from .utils import register_user_for_chat
from django.views.decorators.cache import cache_control

logger = logging.getLogger(__name__)


def reply(status=False, msg="Some error occurred", code=500, dictionary=None):
    if dictionary is None:
        dictionary = {}
    ret = {'status': status, 'message': msg, 'code': code, 'data': dictionary}
    return JsonResponse(ret, status=code)


def index(request):
    return HttpResponse('Hifi')


@csrf_exempt
def verify_user(request):
    """
    POST
    Login for users using digits id
    :param request:
    :return:
    """
    if request.method != 'POST':
        return reply(False, 'Incorrect request method, should be POST', 405)

    u = Users()
    post = request.POST

    # Find digit id in request
    d_id = post.get('digits_id', None)
    if d_id is None:
        return reply(False, 'No digits id provided', 400)

    usr = Users.get_by_digits_id(d_id)
    if usr is None:
        return reply(False, "User with the provided digits id not found", 400)
    # save user's device token on amazon server
    dev_token = post.get('token', None)
    dev_type = post.get('device_type', None)
    if dev_token is not None:
        usr.register_device(dev_token, dev_type)

    # set user status and save
    usr.status = u.FLAG_ACTIVE
    usr.save()

    resp = usr.get_profile_dict()

    # generate session key
    if not request.session.exists(request.session.session_key):
        request.session.create()
    resp['sessionid'] = request.session.session_key

    return reply(True, "Login successful", 200, resp)


@csrf_exempt
@cache_control(max_age=60)
def home(request):
    """
    POST
    :param request:
    :return:
    """
    if request.method != 'POST':
        return reply(False, 'Incorrect request method, should be POST', 405)

    post = request.POST
    u = Users.get_by_digits_id(post.get('digits_id', None))
    if u is None:
        return reply(False, 'digits id is incorrect', 400)

    page = int(post.get('page', 1))
    received_hifis = Hifireceived().fetch_received_hifis(u, page)
    return reply(True, "User's received hydes", 200, received_hifis)


@csrf_exempt
def create_user(request):
    """
    POST
    :param request:
    :return:
    """
    if request.method != 'POST':
        return reply(False, 'Incorrect request method, should be POST', 405)
    u = Users()
    post = request.POST
    d_id = post.get('digits_id', None)
    if d_id is None:
        return reply(False, 'No digits id provided', 400)

    name = post.get('name', None)
    phone = post.get('phone', None)
    email = post.get('email', None)
    if name is None or phone is None or email is None or name == '' or phone == '' or email == '':
        return reply(False, 'Name, email or phone number is missing', 200)

    us = Users.get_by_digits_id(d_id)
    if us is not None:
        return reply(False, "User with given digits id exists", 400)
    elif Users().verified_email_exists(email):
        return reply(False, "User with given email exists", 400)

    dev_token = post.get('token', None)
    dev_type = post.get('device_type', None)
    img = request.FILES.get('photo', None)
    resp = u.create_user(d_id, name, phone, email, dev_token, dev_type, img)
    if not request.session.exists(request.session.session_key):
        request.session.create()
    resp['sessionid'] = request.session.session_key

    return reply(True, 'User created successfully', 200, resp)


@csrf_exempt
def verify_email(request):
    """
    GET
    :param request:
    :return:
    """
    token = request.GET.get('token', None)
    if token is None:
        message = 'Token not provided'
    else:
        try:
            user = Users.objects.get(email_verified=token)
        except ObjectDoesNotExist:
            message = "Incorrect token"
        else:
            if Users().verified_email_exists(user.email):
                message = "User with given email exists"
            else:
                user.email_verified = 0
                user.version += 1
                user.save()
                message = "Email successfully verified"
    return render(request, 'hf/verify_email.html', {'message': message})


@csrf_exempt
def log_out(request):
    """
    GET
    :param request:
    :return:
    """
    if request.method != 'GET':
        return reply(False, 'Incorrect request method, should be GET', 405)
    if request.user.is_authenticated() is False:
        return reply(False, 'User is not logged in', 401)

    u = request.user.users
    u.status = u.FLAG_LOGGED_OUT
    u.save()
    logout(request)
    return reply(True, "Successfully logged out", 200, {})


@csrf_exempt
def create_hifi(request):
    """
    GET
    :param request:
    :return:
    """
    if request.method != 'POST':
        return reply(False, 'Incorrect request method, should be POST', 405)

    post = request.POST
    u = Users.get_by_digits_id(post.get('digits_id', None))
    if u is None:
        return reply(False, 'digits id is incorrect', 400)

    hf_post = post.get('post', None)
    lat = post.get('lat', None)
    lng = post.get('lng', None)

    location = post.get('location', None)
    if hf_post is None or lat is None or lng is None or location is None:
        reply(False, 'Post or location not found', 400)

    repeat = post.get('repeat', 0)
    expiry = post.get('expiry', None)
    expiry = None if expiry == '' else expiry
    condition = post.get('condition', 0)
    attachment = request.FILES.get('attachment', None)
    map_image = request.FILES.get('map_image', None)
    to_users = post.get('hf_userids', None)
    if to_users is None or len(to_users) < 3:
        return reply(False, 'Recipients not found', 400)
    resp = Hifipost().create_hifi(u, hf_post, lat, lng, location, repeat, expiry, attachment, map_image, to_users,
                                 condition)
    return resp


@csrf_exempt
def contact_sync(request):
    """
    :param request:
    contacts string comma separated string of phone numbers
    :return reply:
    """
    if request.method != 'POST':
        return reply(False, 'Incorrect request method, should be POST', 405)

    post = request.POST
    u = Users.get_by_digits_id(post.get('digits_id', None))
    if u is None:
        return reply(False, 'digits id is incorrect', 400)

    ph_nos = post.get('contact', None)
    if ph_nos is None or len(ph_nos) == 0:
        return reply(status=False, msg='contacts not found', code=301)

    f = Friend()
    ret = f.add_friends_by_contact(u, ph_nos)
    return reply(True, str(len(ret)) + ' users found', 200, ret)


@csrf_exempt
@cache_control(max_age=60)
def sent_hifi(request):
    """
    POST
    :param request:
    :return:
    """
    if request.method != 'POST':
        return reply(False, 'Incorrect request method, should be POST', 405)

    post = request.POST
    u = Users.get_by_digits_id(post.get('digits_id', None))
    if u is None:
        return reply(False, 'digits id is incorrect', 400)
    page = int(post.get('page', 1))

    hifis = Hifipost().fetch_sent_hifi(u, page)
    return reply(True, "User's sent hydes", 200, hifis)


@csrf_exempt
def del_hifi(request):
    """
    POST
    :param request:
    :return:
    """
    if request.method != 'POST':
        return reply(False, 'Incorrect request method, should be POST', 405)

    post = request.POST
    u = Users.get_by_digits_id(post.get('digits_id', None))
    if u is None:
        return reply(False, 'digits id is incorrect', 400)
    hifi_id = int(post.get('hifi_id', None))
    try:
        hf = Hifireceived.objects.get(pk=hifi_id, receiver=u)
    except ObjectDoesNotExist as e:
        logger.debug(e.with_traceback(None))
        return reply(False, "Incorrect Hifi id", 400)
    hf.flag = Hifireceived.FLAG_DELETED
    hf.save()
    return reply(True, "Hyde deleted", 200, {'hifi_id': hf.id})


@csrf_exempt
def del_sent_hifi(request):
    """
    POST
    :param request:
    :return:
    """
    if request.method != 'POST':
        return reply(False, 'Incorrect request method, should be POST', 405)

    post = request.POST
    u = Users.get_by_digits_id(post.get('digits_id', None))
    if u is None:
        return reply(False, 'digits id is incorrect', 400)
    hifi_id = int(post.get('hifi_id', None))
    hf = Hifipost.objects.get(pk=hifi_id)
    if hf.sender != u:
        return reply(False, 'Hifi not created by user', 400)

    if post.get('full_delete', None) == 1:
        hf.flag = Hifipost.FLAG_COMPLETELY_DELETED
        hr = Hifireceived.objects.filter(post=hf)
        for h in hr:
            if h.flag == Hifireceived.FLAG_NOT_RECEIVED:
                h.flag = Hifireceived.FLAG_DELETED
                h.save()
    else:
        hf.flag = Hifipost.FLAG_DELETED
    hf.save()

    return reply(True, "Hyde deleted", 200, {'hifi_id': hf.id})


@csrf_exempt
def list_blocked_users(request):
    """
    GET
    :param request:
    :return:
    """
    if request.method != 'POST':
        return reply(False, 'Incorrect request method, should be POST', 405)
    post = request.POST
    u = Users.get_by_digits_id(post.get('digits_id', None))
    if u is None:
        return reply(False, 'digits id is incorrect', 400)
    blocked_users = Users.objects.filter(block_to__from_user=u, block_to__status='1')
    return reply(True, "List of blocked Users", 200, [u.get_profile_dict() for u in blocked_users])


@csrf_exempt
def block_user(request):
    """
    POST
    :param request:
    :return:
    """
    if request.method != 'POST':
        return reply(False, 'Incorrect request method, should be POST', 405)

    post = request.POST
    u = Users.get_by_digits_id(post.get('digits_id', None))
    if u is None:
        return reply(False, 'digits id is incorrect', 400)
    block_id = post.get('user_id', None)
    try:
        to = Users.get_by_hf_id(block_id)
    except ObjectDoesNotExist as e:
        logger.debug(e.with_traceback(None))
        return reply(False, 'User with given id not found', 301)

    block = Block.objects.filter(from_user=u, to_user=to)
    if block.count() < 1:
        block = Block()
        block.to_user = to
        block.from_user = u
        block.status = '1'

        block.block_userid = to.userid
        block.userid = u.userid
        block.created_at = now()
        block.updated_at = now()
        block.save()
    else:
        block = block[0]
        block.status = '1'
        block.save()
    return reply(True, "User blocked", 200, block.get_detail_dict())


@csrf_exempt
def unblock_user(request):
    """
    POST
    :param request:
    :return:
    """
    if request.method != 'POST':
        return reply(False, 'Incorrect request method, should be POST', 405)

    post = request.POST

    u = Users.get_by_digits_id(post.get('digits_id', None))
    if u is None:
        return reply(False, 'digits id is incorrect', 400)

    unblock_id = post.get('user_id', None)
    try:
        bu = Users.get_by_hf_id(unblock_id)
    except ObjectDoesNotExist as e:
        logger.debug(e.with_traceback(None))
        return reply(False, 'Users id is incorrect', 301)

    block = Block.objects.filter(from_user=u, to_user=bu)
    if block.count() < 1:
        return reply(False, 'User is not blocked', 301)
    cnt = 0
    for bl in block:
        cnt += 1
        if cnt == 1:
            bl.status = "0"
            bl.updated_at = now()
            bl.save()
        else:
            bl.delete()
    return reply(True, "User unblocked", 200)


@csrf_exempt
def report_hifi(request):
    """
    :param request:
    :return:
    """
    if request.method != 'POST':
        return reply(False, 'Incorrect request method, should be POST', 405)

    post = request.POST
    u = Users.get_by_digits_id(post.get('digits_id', None))
    if u is None:
        return reply(False, 'digits id is incorrect', 400)

    report_id = post.get('hifi_id', None)
    if report_id is None:
        return reply(False, 'hifi_id is required', 401)
    try:
        hf = Hifireceived.objects.get(post__pk=int(report_id), receiver=u)
    except ObjectDoesNotExist as e:
        logger.debug(e.with_traceback(None))
        return reply(False, 'Hyde with given id and user not found', 301)
    hf.report = Hifireceived.REPORT_REPORTED
    hf.save()
    return reply(True, "Hyde reported", 200)


@csrf_exempt
def update_user_profile(request):
    """
    POST
    :return:
    :param request:
    :return:
    """
    if request.method != 'POST':
        return reply(False, 'Incorrect request method, should be POST', 405)

    post = request.POST
    u = Users.get_by_digits_id(post.get('digits_id', None))
    if u is None:
        return reply(False, 'digits id is incorrect', 400)

    new_digits_id = post.get('new_digits_id', None)
    name = post.get('name', None)
    phone = post.get('phone', None)
    email = post.get('email', None)
    if Users().verified_email_exists(email):
        return reply(False, 'User with given email exists', 400)
    img = request.FILES.get('photo', None)
    remove_image = int(post.get('remove_avatar', 0))
    dev_token = post.get('token', None)
    dev_type = post.get('device_type', None)
    us = Users.get_by_digits_id(new_digits_id)
    if us is not None:
        return reply(False, 'User with new digits id exists', 400)
    updated = u.update_profile(name, phone, email, img, dev_token, dev_type, new_digits_id, remove_image)
    if len(updated) > 0:
        return reply(True, ', '.join(updated) + ' in user profile successfully updated', 200,
                     u.get_profile_dict())
    else:
        return reply(False, 'Nothing to update', 422)


@csrf_exempt
def update_user_location(request):
    """
    POST
    :return:
    :param request:
    :return:
    """
    if request.method != 'POST':
        return reply(False, 'Incorrect request method, should be POST', 405)

    post = request.POST
    u = Users.get_by_digits_id(post.get('digits_id', None))
    if u is None:
        return reply(False, 'digits id is incorrect', 400)
    if u.status != Users.FLAG_ACTIVE:
        u.status = Users.FLAG_ACTIVE
        u.save()

    token = post.get('token', None)
    device_type = post.get('device_type', None)
    if u.device_arn is None and token is not None and device_type is not None:
        u.register_device(token, device_type)

    if token is not None and u.device_token is not None and u.device_token != '':
        if u.device_token != token:
            NotificationHelper().silent_token_mismatch_push(token, device_type)
            logger.info('device token mismatch')
            logger.info('Registered token' + str(u.device_token))
            logger.info('Newly received token ' + str(token))
            logger.info(u)
            return reply(False, 'Different device token', 400)

    old_coord = None
    tim = now()
    try:
        ul = Location.objects.get(user=u)
        time_diff = now() - ul.updated_at
        if time_diff.days == 0 and time_diff.seconds <= 20:
            old_coord = {'lat': float(ul.lat), 'lng': float(ul.lng)}
        ul.average = (ul.average * ul.total + time_diff.seconds) / (ul.total + 1)
        ul.total += 1
    except ObjectDoesNotExist:
        ul = Location()
        ul.user = u
        ul.userid = u.userid
        ul.created_at = tim

    ul.lat = post.get('lat', None)
    ul.lng = post.get('lng', None)
    ul.loc_coord = 'POINT( ' + ul.lat + ' ' + ul.lng + ')'
    ul.updated_at = tim
    ul.save()
    ul.send_interest_notification()
    ul.process_location_update(old_coord)

    return reply(True, "User's location successfully updated", 200)


@csrf_exempt
def activity(request):
    """
    :param request:
    contacts string comma separated string of phone numbers
    :return reply:
    """
    if request.method != 'POST':
        return reply(False, 'Incorrect request method, should be POST', 405)

    post = request.POST
    u = Users.get_by_digits_id(post.get('digits_id', None))
    if u is None:
        return reply(False, 'digits id is incorrect', 400)

    page = int(post.get('page', 1))
    hf = Hifireceived()
    new_list = hf.get_activity_feed(u, page)

    return reply(True, "User's activity feed", 200, new_list)


@csrf_exempt
def update_user_status(request):
    """
    GET
    :param request:
    :return:
    """
    if request.method != 'POST':
        return reply(False, 'Incorrect request method, should be POST', 405)

    post = request.POST
    u = Users.get_by_digits_id(int(post.get('digits_id', None)))
    if u is None:
        return reply(False, 'Incorrect digits id', 400)

    status = int(post.get('status', None))
    if status != 0 and status != 1 and status != 2 and status != 3:
        return reply(False, 'Invalid status', 400)
    u.status = status
    u.save()
    return reply(True, 'User status successfully updated', 200)


@csrf_exempt
def view_logs(request):
    """
    :param request:
    :return:
    """
    y = ''
    count = 0
    file_name = settings.BASE_DIR + '/' + "hifi.log"
    try:
        f = open(file_name, 'r')
    except FileNotFoundError:
        return HttpResponse('Log file not found.')
    one_message = []
    for line in reversed(list(f)):
        count += 1
        if count > 20000:
            break
        one_message.append(line.rstrip() + '<br>')
        if line[0] == '[':
            for l in reversed(one_message):
                y += l
            one_message = []
    f.close()
    y = '<meta http-equiv="refresh" content="600; URL=#">' + y
    return HttpResponse(y)


@csrf_exempt
def get_user_version(request):
    """
    POST
    :param request:
    :return:
    """
    if request.method != 'POST':
        return reply(False, 'Incorrect request method, should be POST', 405)

    post = request.POST
    ident = post.get('hf_user_id', None)
    if ident is None:
        ident = post.get('digits_id', None)
        if ident is None:
            return reply(True, 'digits id not found', 200, {})

    ident = ident.split(',')
    ret = []
    for ide in ident:
        if 'HF' in ide:
            u = Users.get_by_hf_id(ide)
        else:
            u = Users.get_by_digits_id(ide)

        if u is not None:
            ret.append(u)
    if len(ret) == 0:
        return reply(False, 'User not found', 200)

    return reply(True, 'User details', 200, u.get_profile_dict())


@csrf_exempt
def list_interests(request):
    """
    :param request:
    :return reply:
    """
    if request.method != 'POST':
        return reply(False, 'Incorrect request method, should be POST', 405)

    post = request.POST
    u = Users.get_by_digits_id(post.get('digits_id', None))
    if u is None:
        return reply(False, 'Incorrect user id', 400)

    resp = UserInterest().get_user_subscription(u)
    return reply(True, "List of interests", 200, resp)


@csrf_exempt
def subscribe_interest(request):
    if request.method != 'POST':
        return reply(False, 'Incorrect request method, should be POST', 405)

    post = request.POST
    u = Users.get_by_digits_id(post.get('digits_id', None))
    if u is None:
        return reply(False, 'Incorrect digits id', 400)

    interest_id = post.get('interest_id', None)
    if interest_id is None:
        return reply(False, 'interest_id not found', 422)

    status = int(post.get('status', None))
    if status not in [UserInterest.STATUS_SUBSCRIBED, UserInterest.STATUS_NOT_SUBSCRIBED]:
        return reply(False, 'invalid status', 422)

    msg = 'Successfully subscribed' if status == UserInterest.STATUS_SUBSCRIBED else 'Successfully unsubscribed'
    inter = Interest.get_by_id(interest_id)
    if inter is None:
        return reply(False, 'Interest with given id not found', 422)

    resp = UserInterest.subscribe_user(u, inter, status)
    if resp is True:
        return reply(True, msg, 200)
    else:
        return reply()


@csrf_exempt
def verify_api(request):
    """
    POST
    :param request:
    :return:
    """

    return render(request, 'hf/verify_api.html', {})


@csrf_exempt
def interest(request):
    """
        POST
        :param request:
        :return:
        """
    if request.method != 'POST':
        return reply(False, 'Incorrect request method, should be POST', 405)

    post = request.POST
    u = Users.get_by_digits_id(int(post.get('digits_id', None)))
    if u is None:
        return reply(False, 'Incorrect digits id', 400)

    lat = post.get('lat', None)
    lng = post.get('lng', None)
    distance = 1000 * float(post.get('distance', None))
    if lat is None or lng is None or distance is None:
        return reply(False, 'Incorrect parameters', 400)
    ints = InterestData().find_nearby_interests(lat, lng, u.id, distance)
    return reply(True, 'Nearby interests', 200, ints)


@csrf_exempt
def view_post(request):
    if request.method != 'POST':
        return reply(False, 'Incorrect request method, should be POST', 405)

    post = request.POST
    u = Users.get_by_digits_id(int(post.get('digits_id', None)))
    if u is None:
        return reply(False, 'Incorrect digits id', 400)
    post_id = post.get('post_id', None)
    if post_id is None:
        return reply(False, 'post id not found', 422)
    post = Hifireceived().get_post_details(post_id, u)
    if type(post) == tuple:
        return reply(False, post[1], 400)
    return reply(True, 'Hyde data', 200, post)


@csrf_exempt
def like_post(request):
    if request.method != 'POST':
        return reply(False, 'Incorrect request method, should be POST', 405)

    post = request.POST
    u = Users.get_by_digits_id(int(post.get('digits_id', None)))
    if u is None:
        return reply(False, 'Incorrect digits id', 400)

    post_id = post.get('post_id', None)
    if post_id is None:
        return reply(False, 'post id not found', 422)

    like_flag = int(post.get('like_flag', None))
    if like_flag is None or like_flag not in [Hifireceived.LIKED, Hifireceived.NOT_LIKED]:
        return reply(False, 'like flag incorrect', 422)

    post = Hifireceived().set_like_flag(post_id, u, like_flag)
    if type(post) == tuple:
        return reply(False, post[1], 400)
    return reply(True, 'successfully liked', 200, post)


@csrf_exempt
def acknowledge_notification(request):
    return reply(True, 'This api is deprecated. Do not use.', 200)
    # if request.method != 'POST':
    #     return reply(False, 'Incorrect request method, should be POST', 405)
    #
    # post = request.POST
    # u = Users.get_by_digits_id(int(post.get('digits_id', None)))
    # if u is None:
    #     return reply(False, 'Incorrect digits id', 400)
    #
    # post_id = post.get('post_id', None)
    # if post_id is None:
    #     return reply(False, 'post id not found', 422)
    # post = Hifireceived().notify_sender(Hifireceived.objects.filter(post_id=post_id, receiver=u).select_related('post'))
    #
    # return reply(True, 'Hyde received', 200, post)


@csrf_exempt
def send_chat_push(request):
    if request.method != 'POST':
        return reply(False, 'Incorrect request method, should be POST', 405)

    post = request.POST
    u = Users.get_by_digits_id(post.get('from', None))
    if u is None:
        return reply(False, 'Incorrect digits id', 400)

    to_user = Users.get_by_digits_id(post.get('to', None))
    if to_user is None:
        return reply(False, 'Post id not found', 422)

    if to_user.status == Users.FLAG_LOGGED_OUT:
        return reply(False, 'User is logged out', 422)

    message = post.get('body', None)
    avt = ''
    if u.avatar.name != '' and u.avatar.name is not None:
        avt = settings.FILES_PREFIX + '/' + str(u.avatar.name)
    resp = NotificationHelper().chat_push(to_user.device_arn, u.fullname, avt, message)
    if type(resp) == tuple:
        if resp[1] == 'EndpointDisabled':
            to_user.delete_device_arn()
    return reply(True, '', 200)
