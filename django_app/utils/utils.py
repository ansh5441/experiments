import base64
import datetime
import hashlib
import logging
import random
import sys
from io import BytesIO

import requests
import sleekxmpp
from PIL import Image as Img
from django.core.files.base import ContentFile
from django.utils.timezone import now
from pytz import UnknownTimeZoneError
from requests.auth import HTTPBasicAuth
from timezonefinder import TimezoneFinder

logger = logging.getLogger(__name__)


def read_tail(f, lines=20):
    total_lines_wanted = lines
    block_size = 1024
    f.seek(0, 2)
    block_end_byte = f.tell()
    lines_to_go = total_lines_wanted
    block_number = -1
    blocks = []  # blocks of size block_size, in reverse order starting
    # from the end of the file
    while lines_to_go > 0 and block_end_byte > 0:
        if block_end_byte - block_size > 0:
            # read the last block we haven't yet read
            f.seek(block_number * block_size, 2)
            blocks.append(f.read(block_size))
        else:
            # file too small, start from begining
            f.seek(0, 0)
            # only read what was not read
            blocks.append(f.read(block_end_byte))
        lines_found = blocks[-1].count('\n')
        lines_to_go -= lines_found
        block_end_byte -= block_size
        block_number -= 1
    all_read_text = ''.join(reversed(blocks))
    return '<br>'.join(all_read_text.splitlines()[-total_lines_wanted:])


def desc(o):
    string = '\n' + '-' * 120 + '\n|' + "_" * 10 + "Type of o is - " + str(
        type(o)) + "_" * 40 + '|\n|' + "_" * 10 + "Printing object" + "_" * 54 + '|' + '\n'
    string += str(o) + '\n'
    string += '|' + "_" * 10 + "Members of object are" + "_" * 48 + '|' + '\n'
    string += str(dir(o)) + '\n'
    string += '-' * 120 + '\n'
    print(string)
    return string


def get_thumb_bytes(file, size=(300, 300)):
    pic = Img.open(file)
    pic.thumbnail(size)
    new_image_io = BytesIO()
    django_type = file.content_type

    if django_type == 'image/jpeg':
        pli_type = 'jpeg'
    elif django_type == 'image/png':
        pli_type = 'png'
    else:
        pli_type = 'jpeg'
    try:
        pic.save(new_image_io, pli_type)
    except Exception as e:
        logger.error(e.with_traceback(None))
        return None
    return new_image_io.getvalue()


def get_image_from_url(url):

    return


def make_thumbnail(file, size=(200, 200)):
    image_bytes = get_thumb_bytes(file, size)
    ret = ContentFile(image_bytes)
    ret.name = file.name
    return ret


def get_as_base64(url):
    b64 = ''
    try:
        b64 = base64.b64encode(requests.get(url).content).decode()
    except Exception as e:
        logger.error(e.with_traceback(None))
    return b64


def get_unique_token():
    t = str(now())
    m = hashlib.md5(str.encode(t + str(random.randint(0, 9999999))))
    return m.hexdigest()


def get_file_name(fil):
    t = str(datetime.datetime.utcnow())
    m = hashlib.md5(str.encode(t + str(random.randint(0, 9999999))))
    return "t" + t[5:19] + "i" + m.hexdigest()[:16] + '.' + fil.name.split('.')[-1]


def get_day_num():
    day_num = now().weekday() + 2
    if day_num == 8:
        day_num = 1
    return str(day_num)


def find_timezone(lat, lng):
    tf = TimezoneFinder()
    lat = float(lat)
    lng = float(lng)

    try:
        timezone_name = tf.timezone_at(lng=lng, lat=lat)
        if timezone_name is None:
            timezone_name = tf.closest_timezone_at(lng=lng, lat=lat)
            if timezone_name is None:
                timezone_name = 'UTC'
                # maybe even increase the search radius when it is still None

    except ValueError:
        timezone_name = 'UTC'
    except UnknownTimeZoneError:
        timezone_name = 'UTC'
    return timezone_name


# Print iterations progress
def print_progress(iteration, total, prefix='', suffix='', decimals=3, bar_length=100):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : number of decimals in percent complete (Int)
        bar_length   - Optional  : character length of bar (Int)
    """
    filled_length = int(round(bar_length * iteration / float(total)))
    percents = round(100.00 * (iteration / float(total)), decimals)
    start = '█'
    remaining = '░'
    # start = '1'
    # remaining = '0'
    bar = start * filled_length + remaining * (bar_length - filled_length)
    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),
    sys.stdout.flush()
    if iteration == total:
        sys.stdout.write('\n')
        sys.stdout.flush()


# class RegisterCommand(sleekxmpp.ClientXMPP):
#     """
#     A simple SleekXMPP bot that uses admin commands to
#     add a new user to a server.
#     """
#
#     def __init__(self, jid, password, command, uname, passwd):
#         sleekxmpp.ClientXMPP.__init__(self, jid, password)
#         self.command = command
#         self.uname = uname
#         self.passwd = passwd
#         self.add_event_handler("session_start", self.start)
#
#     def start(self, event):
#         """
#         Process the session_start event.
#         Typical actions for the session_start event are
#         requesting the roster and broadcasting an initial
#         presence stanza.
#         Arguments:
#             event -- An empty dictionary. The session_start
#                      event does not provide any additional
#                      data.
#         """
#
#         def command_success(iq, session):
#             if iq['command']['form']:
#                 for var, field in iq['command']['form']['fields'].items():
#                     print('%s: %s' % (var, field['value']))
#             if iq['command']['notes']:
#                 print('Command Notes:')
#                 for note in iq['command']['notes']:
#                     print('%s: %s' % note)
#             self.disconnect()
#
#         def command_error(iq, session):
#             print('Error completing command')
#             print('%s: %s' % (iq['error']['condition'],
#                               iq['error']['text']))
#             self['xep_0050'].terminate_command(session)
#             self.disconnect()
#
#         def process_form(iq, session):
#             form = iq['command']['form']
#             answers = {'accountjid': self.uname, 'password': self.passwd, 'password-verify': self.passwd}
#
#             for var, field in form['fields'].items():
#                 if var == 'FORM_TYPE':
#                     answers['FORM_TYPE'] = field['value']
#             form['type'] = 'submit'
#             form['values'] = answers
#             session['next'] = command_success
#             session['payload'] = form
#
#             self['xep_0050'].complete_command(session)
#
#         session = {'next': process_form,
#                    'error': command_error}
#
#         command = self.command.replace('-', '_')
#         handler = getattr(self['xep_0133'], command, None)
#         if handler:
#             handler(session={
#                 'next': process_form,
#                 'error': command_error
#             })
#         else:
#             print('Invalid command name: %s' % self.command)
#             self.disconnect()
# #
# #
# def register_user_for_chat(**kwargs):
#     xmp = RegisterCommand('admin@convers.im', 'Hifi1234', 'add-user', kwargs.get('digits_id') + "@convers.im",
#                           kwargs.get('digits_id'))
#     xmp.register_plugin('xep_0133')
#     if xmp.connect(('convers.im', 5222), reattempt=True, use_tls=False):
#         xmp.process(block=True)
#         return True
#     else:
#         return False


def register_user_chat_http(digits_id):
    server = "localhost"
    virtual_host = "ex"
    url = "http://%s:5280/admin/server/%s/users/" % (server, virtual_host)
    auth = HTTPBasicAuth("admin@ex", "admin")
    data = {
        'newusername': digits_id,
        'newuserpassword': digits_id,
        'addnewuser': "Add User"
    }
    resp = requests.post(url, data=data, auth=auth)


if __name__ == "__main__":
    pass
