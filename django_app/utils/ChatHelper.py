import xml
from pprint import pprint

import requests
import sleekxmpp
from django.conf import settings
from django.utils.timezone import now

import logging
import threading
import sleekxmpp
from io import BytesIO, StringIO

from sleekxmpp import Iq
from sleekxmpp.jid import JID
from sleekxmpp.xmlstream import ET
from sleekxmpp.exceptions import XMPPError
from sleekxmpp.plugins import BasePlugin, register_plugin
from sleekxmpp.stanza.roster import Roster, RosterItem

# from utils.utils import print_progress
from PIL import Image as Img

logger = logging.getLogger(__name__)


class RegisterCommand(sleekxmpp.ClientXMPP):
    """
    A simple SleekXMPP bot that uses admin commands to
    add a new user to a server.
    """

    def __init__(self, jid, password, command, uname, passwd):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        self.command = command
        self.uname = uname
        self.passwd = passwd
        self.add_event_handler("session_start", self.start)

    def start(self, event):
        """
        Process the session_start event.
        Typical actions for the session_start event are
        requesting the roster and broadcasting an initial
        presence stanza.
        Arguments:
            event -- An empty dictionary. The session_start
                     event does not provide any additional
                     data.
        """

        def command_success(iq, session):
            if iq['command']['form']:
                for var, field in iq['command']['form']['fields'].items():
                    print('%s: %s' % (var, field['value']))
            if iq['command']['notes']:
                print('Command Notes:')
                for note in iq['command']['notes']:
                    print('%s: %s' % note)
            self.disconnect()

        def command_error(iq, session):
            print('Error completing command')
            print('%s: %s' % (iq['error']['condition'],
                              iq['error']['text']))
            self['xep_0050'].terminate_command(session)
            self.disconnect()

        def process_form(iq, session):
            form = iq['command']['form']
            answers = {'accountjid': self.uname, 'password': self.passwd, 'password-verify': self.passwd}

            for var, field in form['fields'].items():
                if var == 'FORM_TYPE':
                    answers['FORM_TYPE'] = field['value']
            form['type'] = 'submit'
            form['values'] = answers
            session['next'] = command_success
            session['payload'] = form

            self['xep_0050'].complete_command(session)

        session = {'next': process_form,
                   'error': command_error}

        command = self.command.replace('-', '_')
        handler = getattr(self['xep_0133'], command, None)
        if handler:
            handler(session={
                'next': process_form,
                'error': command_error
            })
        else:
            print('Invalid command name: %s' % self.command)
            self.disconnect()


class AdminCommands(sleekxmpp.ClientXMPP):
    """
    A simple SleekXMPP bot that uses admin commands in various ways
    """

    def __init__(self, command, **kwargs):
        sleekxmpp.ClientXMPP.__init__(self, 'admin@convers.im', 'Hifi1234')
        self.command = command
        self._kwargs = kwargs
        self.ret = None

    def discon(self, ret):
        url = settings.BASE_URL + '/update_user_status/'
        pst = {'digits_id': self._kwargs.get('digits_id')}
        if ret == 'Online':
            pst['status'] = 1  # Background
        else:
            pst['status'] = 2  # Terminated
        requests.post(url, pst)

    def execute(self):
        def command_success(iq, session):
            if iq['command']['form']:
                for var, field in iq['command']['form']['fields'].items():
                    if self.command == 'get-user-lastlogin':
                        print('%s: %s' % (var, field['value']))
                        if var == 'lastlogin':
                            self.ret = field['value']
                self.discon(self.ret)
            if iq['command']['notes']:
                print('Command Notes:')
                for note in iq['command']['notes']:
                    print('%s: %s' % note)
            self.disconnect()

        def command_error(iq, session):
            print('Error completing command')
            print('%s: %s' % (iq['error']['condition'],
                              iq['error']['text']))
            self['xep_0050'].terminate_command(session)
            self.disconnect()

        def process_form(iq, session):
            form = iq['command']['form']
            if self.command == 'get-user-lastlogin':
                jid = str(self._kwargs.get('digits_id')) + '@convers.im'
                answers = {'accountjid': jid}

            for var, field in form['fields'].items():
                if var == 'FORM_TYPE':
                    answers['FORM_TYPE'] = field['value']
            form['type'] = 'submit'
            form['values'] = answers
            session['next'] = command_success
            session['payload'] = form
            session['block'] = True
            self['xep_0050'].complete_command(session)
            self.disconnect()

        command = self.command.replace('-', '_')
        handler = getattr(self['xep_0133'], command, None)
        if handler:
            handler(session={'next': process_form,
                             'error': command_error, 'block': True})
            return self.ret

        else:
            print('Invalid command name: %s' % self.command)
            self.disconnect()


class UserClient(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password, **kwargs):
        super(UserClient, self).__init__(jid, password)
        self.register_plugin('xep_0172')
        self.register_plugin('xep_0030')
        self.register_plugin('xep_0084')
        self.register_plugin('xep_0153')
        self.register_plugin('xep_0054')
        self.register_plugin('xep_0163')
        self.register_plugin('xep_0060')
        self.register_plugin('xep_0191')
        self.add_event_handler('session_start', self.session_start)

    def session_start(self, event):
        # self.send_presence()
        self.schedule('end', 5, self.disconnect, kwargs={'wait': True})

    def set_vcard(self, **kwargs):
        name = kwargs.get('name', None)
        image = kwargs.get('image', None)
        if name is None and image is None:
            return
        vcard = self['xep_0054'].stanza.VCardTemp()
        if name is not None:
            vcard['FN'] = name
            vcard['NICKNAME'] = name
        vcard['JABBERID'] = self.boundjid.bare
        if image is not None:
            vcard['PHOTO']['BINVAL'] = image
            vcard['PHOTO']['TYPE'] = 'image/jpeg'
        self['xep_0054'].publish_vcard(vcard)

    def get_blocked(self):
        bl = self['xep_0191'].stanza.BlockList()
        print(self['xep_0191'].get_blocked())
        return bl

    def get_online_status(self, jid):
        items = self['xep_0030'].get_info(jid=jid, iterator=True)

        return items


class ChatHelper:
    def __init__(self, digits_id):
        self.dns = 'convers.im'
        self.password = str(digits_id)
        self.jabber_id = self.jidfy(digits_id)
        self.xmp = None

    def connect(self):
        xmp = UserClient(self.jabber_id, self.password)
        if xmp.connect((self.dns, 5222), reattempt=True, use_tls=True):
            xmp.process(block=False)
            self.xmp = xmp
            return xmp
        return False

    def jidfy(self, digits_id):
        return str(digits_id) + '@' + self.dns

    def change_user_nick(self, **kwargs):
        """
        :param  kwargs: nick: new name of the user
        :return:
        """
        nick = kwargs.get('nick', None)
        if nick is None:
            return False
        if self.xmp is None:
            xmp = self.connect()
        else:
            xmp = self.xmp
        if xmp is False:
            return False
        roster = xmp.get_roster(block=True)
        roster = roster.get('roster').get_items()
        for k in roster.keys():
            ch = ChatHelper(k.user)
            xmp2 = ch.connect()
            if xmp2 is False:
                continue
            xmp2.update_roster(self.jabber_id, name=nick, block=False)
        return True

    def sync_roster(self, **kwargs):
        # TODO - speed up this process
        """
        :param kwargs:  digits_id_list: dictionary of friends' digits ids and names
                        name: user's name
        :return:
        """
        # print(self.jabber_id)
        digits_id_dict = kwargs.get('digits_id_dict', None)
        if digits_id_dict is None:
            return False, "digits_id_list not found"
        if self.xmp is None:
            xmp = self.connect()
        else:
            xmp = self.xmp
        if xmp is False:
            return False
        # print(digits_id_dict)

        roster = xmp.get_roster(block=True)
        roster = roster.get('roster').get_items()
        for k in roster.keys():
            if k.user not in digits_id_dict.keys():
                xmp.update_roster(self.jidfy(k.user), subscription='remove', block=False)
                ch = ChatHelper(str(k.user))
                xmp2 = ch.connect()
                xmp2.update_roster(self.jabber_id, subscription='remove', block=False)
            digits_id_dict.pop(k.user, None)
        for k in digits_id_dict.keys():
            to_user_jid = self.jidfy(k)
            xmp.send_presence(pto=to_user_jid, ptype='subscribe')
            xmp.update_roster(to_user_jid, name=digits_id_dict[k], block=False, subscription='from')

            ch = ChatHelper(str(k))
            xmp2 = ch.connect()
            xmp2.send_presence(pto=self.jabber_id, ptype='subscribe')
            xmp2.update_roster(self.jabber_id, name=kwargs.get('name'), block=False, subscription='from')

    def set_user_vcard(self, **kwargs):
        """
        :param kwargs: name, image, digits_id
        :return:
        """
        if self.xmp is None:
            xmp = self.connect()
        else:
            xmp = self.xmp
        xmp.set_vcard(**kwargs)


def send_hifi_as_chat(**kwargs):
    from_user_jid = kwargs.get('from_user_did') + '@convers.im'
    to_user_jid = kwargs.get('to_user_did') + '@convers.im'
    post = kwargs.get('post', '')
    xmp = UserClient(from_user_jid, kwargs.get('from_user_did'))
    if xmp.connect(('convers.im', 5222), reattempt=True, use_tls=True):
        xmp.process()
        xmp.send_message(to_user_jid, post)
        # xmp.disconnect(wait=True)


def register_user_for_chat(**kwargs):
    """
    :param kwargs:  register_user_for_chat
    :return:
    """
    jid = str(kwargs.get('digits_id')) + '@convers.im'
    passwd = str(kwargs.get('digits_id'))
    xmp = RegisterCommand('admin@convers.im', 'Hifi1234', 'add-user', jid, passwd)
    xmp.register_plugin('xep_0133')

    if xmp.connect(('convers.im', 5222), reattempt=True, use_tls=False):
        xmp.process(block=True)
        return True
    else:
        return False


def set_user_vcard(**kwargs):
    """
    :param kwargs: name, image, digits_id
    :return:
    """
    # logging.basicConfig(level=2, format='%(levelname)-8s %(message)s')
    digits_id = kwargs.get('digits_id', None)
    if digits_id is None:
        return False, "digits id is None"
    name = kwargs.get('name', None)
    image = kwargs.get('image', None)

    xmp = UserClient(digits_id + '@convers.im', digits_id)
    if xmp.connect(('convers.im', 5222), reattempt=True, use_tls=False):
        xmp.process(wait=True)
        xmp.set_vcard(name=name, image=image)
        xmp.disconnect(wait=True)
        return True
    else:
        return False, "Could not connect to server"


def set_user_vcards_bulk():
    dig_arr = [('714496010521866241', 'profile_pics/t08-12_181308i9e8a3e941510d2b7.jpg', 'Hifi')]
    count = 0
    tot = len(dig_arr)
    for i in dig_arr:
        count += 1
        if count < 90:
            continue
        img_byte = None
        if i[1] != '':
            try:
                rr = requests.get('http://hifiprodbkt.s3.amazonaws.com/' + i[1])
            except:
                print(i[1])
                continue
            try:
                pic = Img.open(BytesIO(rr.content))
            except:
                print(i[1])
            else:
                pic.thumbnail((200, 200))
                new_image_io = BytesIO()
                pic.save(new_image_io, 'jpeg')
                img_byte = new_image_io.getvalue()

        # print_progress(count, tot)
        set_user_vcard(name=i[2], image=img_byte, digits_id=i[0])


class AsyncChatCommands(threading.Thread):
    def __init__(self, **kwargs):
        threading.Thread.__init__(self)
        self._kwargs = kwargs
        self.command = kwargs.get('command', None)
        self.digits_id = kwargs.get('digits_id', None)

    def run(self):
        if self.command is None:
            return
        elif self.command == 'set_user_vcard':
            set_user_vcard(**self._kwargs)
        elif self.command == 'change_user_nick':
            ch = ChatHelper(self.digits_id)
            ch.change_user_nick(**self._kwargs)
        elif self.command == 'sync_roster':
            ch = ChatHelper(self.digits_id)
            ch.sync_roster(**self._kwargs)
        elif self.command == 'send_hifi_as_chat':
            send_hifi_as_chat(**self._kwargs)


def set_user_status(digits_id):
    xmp = AdminCommands('get-user-lastlogin', digits_id=digits_id)
    xmp.register_plugin('xep_0133')

    if xmp.connect(('convers.im', 5222), reattempt=True, use_tls=False):
        xmp.process(block=False)
        xmp.execute()


if __name__ == "__main__":
    pass
    # c = ChatHelper('1')
    # c.change_user_nick('Suresh')
    # print(1)
    # import random
    #
    # x = random.randint(1, 100)
    # print(x)
    # background = AsyncChatCommands(digits_id='1', from_user_did='1',
    #                                to_user_did='5', post='haha post' + str(x),
    #                                command='send_hifi_as_chat')
    # background.start()
    # print(2)
    # send_hifi_as_chat(from_user_did='5', to_user_did='1', from_user_name='from_user_name', to_user_name='to_user_name',
    #                   post='new post')
    # logging.basicConfig(level=2, format='%(levelname)-8s %(message)s')

    # set_user_vcard(digits_id='1', name="The first user",
    #                image='http://hifiprodbkt.s3.amazonaws.com/profile_pics/t08-16_061538ie7ba778837eb67a5.jpg')
    # client = UserClient('4789370132@convers.im','4789370132')
    # digits_id = '1'
    # xmp = UserClient(digits_id + '@convers.im', digits_id)
    # if xmp.connect(('convers.im', 5222), reattempt=True, use_tls=False):
    #     xmp.process(wait=True)
    #     resp = xmp.get_online_status(digits_id + '@convers.im')
    #
    #     print(resp)

    q = register_user_for_chat(digits_id=4)
    print(q)
