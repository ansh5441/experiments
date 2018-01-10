from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views.decorators.csrf import csrf_exempt

from hf.views import reply


@csrf_exempt
def create_campaign(request):
    if request.method != 'POST':
        return reply(False, 'Incorrect request method, should be POST', 405)
    post = request.POST
    file_name = settings.BASE_DIR + '/' + "campaign.log"
    f = open(file_name, 'a')
    keys = ['type', 'name', 'budget', 'daily_cap', 'proximity', 'message', 'has_image', 'image_path', 'start_date',
            'end_date', 'start_time', 'end_time', 'repeat', 'interest', 'store_id']
    strin = ''
    for k in keys:
        strin += k + ": " + post.get(k, '') + '\n'
    strin += "_" * 120 + '\n'
    f.write(strin)
    f.close()
    return reply(True, 'Campaign successfully created', 200)


@csrf_exempt
def view_campaign(request):
    """
    :param request:
    :return:
    """
    if request.method != 'GET':
        return reply(False, 'Incorrect request method, should be GET', 405)
    y = ''
    file_name = settings.BASE_DIR + '/' + "campaign.log"
    try:
        f = open(file_name, 'r')
    except FileNotFoundError:
        return HttpResponse('')
    for line in list(f):
        y += line.rstrip() + '<br>'
    f.close()
    return HttpResponse(y)


def signup(request):
    pass


def login(request):
    pass


def business_edit(request):
    pass


def business_store_add(request):
    pass


def business_payement_add(request):
    pass


def business_store_add(request):
    pass
