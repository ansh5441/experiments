import gzip
import os
import random
import shutil
from datetime import datetime
from logging import getLogger

from django.conf import settings
from django.utils.timezone import now


class LoggingMiddleware(object):
    def __init__(self):
        # arguably poor taste to use django's logger
        self.logger = getLogger(__name__)
        filename = settings.LOGGING['handlers']['file']['filename']
        self.dir_name = os.path.join(os.path.dirname(filename), 'logs')

    def process_request(self, request):
        log = ''
        meta_keys = ['PATH_INFO', 'HTTP_USER_AGENT', 'SERVER_PORT', 'REQUEST_METHOD', 'REMOTE_ADDR',
                     'CONTENT_LENGTH', 'SERVER_ADDR']
        arr3 = [str(key.lower()) + ": " + str(request.META.get(key, 'NOT FOUND')) for key in meta_keys]
        log += '\n\n<b>HEADERS</b>\n' + '\n'.join(arr3)

        cookies = [str(k) + ": " + str(request.COOKIES[k]) for k in request.COOKIES.keys()]
        log += '\n\n<b>COOKIES</b>\n' + '\n'.join(cookies) if len(cookies) > 0 else '\n\nNO COOKIES\n'

        if request.method == "POST":
            arr = [str(k) + ": " + str(request.POST[k]) for k in request.POST.keys()]
            log += '\n\n<b>POST REQUEST DATA</b>\n' + '\n'.join(arr)
            files_arr = [str(k) + ": " + str(request.FILES[k].name) + " : " + str(request.FILES[k].size) for
                         k in request.FILES.keys()]

            log += '\n\n<b>FILES</b>\n' + '\n'.join(files_arr) if len(files_arr) > 0 else '\n\nNO FILES\n'
            try:
                self.logger.info(log)
            except Exception as e:
                print(e.with_traceback(None))
        if random.random() < 0.05:
            self.rotate_log()

    def rotate_log(self):
        filename = settings.LOGGING['handlers']['file']['filename']
        if os.path.getsize(filename) < 25000000:
            return

        new_name = os.path.join(self.dir_name,
                                str(now()).replace(" ", '_').replace(":", '_')[:18] + os.path.basename(filename))
        shutil.copy(filename, new_name)

        with open(new_name, 'rb') as f_in:
            with gzip.open(new_name + '.gz', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        os.remove(new_name)
        f = open(filename, 'w')
        f.write('\n')
        f.close()

        self.delete_old_files()

    def delete_old_files(self):
        for f in os.listdir(self.dir_name):
            try:
                t = datetime(year=int(f[:4]), month=int(f[5:7]), day=int(f[8:10]))
            except:
                continue
            time_diff = now().replace(tzinfo=None) - t
            if time_diff.days > 21:
                os.remove(os.path.join(self.dir_name, f))
