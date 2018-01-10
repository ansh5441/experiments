import json
import os
from django.test import Client
from django.test import TestCase

from .models import Hifipost, Users, Hifireceived


# db = MySQLdb.connect(user="root", passwd="'", db="test_hifi")
# cur = db.cursor()

def select_star(tab, c):
    c.execute("""SELECT * FROM """ + tab)
    columns = c.fetchall()
    ret = []
    for col in columns:
        ret.append(col)
    return ret


class TestViews(TestCase):
    def setUp(self):
        print('setup')
        c = Client()
        self.user = []
        fp = open('media/test.jpg', 'rb')
        # create 4 users
        response = c.post('/create_user/', {'digits_id': 1, 'name': 'Sampat Laal', 'phone': '9911111111', 'photo': fp,
                                            'email': 'yederese@storyboard.co'})
        self.user.append(response.json()['data'])

        response = c.post('/create_user/', {'digits_id': 2, 'name': 'Sarweshwar Dayal Saxena', 'phone': '9922222222', 'photo': fp,
                                            'email': 'ramdhari_singh_dinkar@storyboard.co'})
        self.user.append(response.json()['data'])

        response = c.post('/create_user/', {'digits_id': 3, 'name': 'Badshaah', 'phone': '9933333333', 'photo': fp,
                                            'email': 'don_kabir_khan@storyboard.co'})
        self.user.append(response.json()['data'])

        response = c.post('/create_user/', {'digits_id': 4, 'name': 'Rekha Mishra', 'phone': '9944444444', 'photo': fp,
                                            'email': 'rekha_bindu@storyboard.co'})
        self.user.append(response.json()['data'])

        c.post('/create_hifi/', {
            'lat': '28.0198', 'lng': "-82.739817", 'location': "rr", 'post': 'hello all',
            'hf_userids': self.user[0]['userid']
        })

        response = c.post('/create_hifi/', {
            'lat': '28.0198', 'lng': "-82.739817", 'location': "rr",
            'post': 'hello all', 'hf_userids': ",".join([str(k['userid']) for k in self.user])
        })
        fp.close()
        r = response.json()
        self.post = r['data']

    def test_request_methods(self):
        print('test request methods')
        c = Client()
        response = c.get('/verify_user/')
        self.assertEqual(response.json()['message'], 'Incorrect request method, should be POST')
        response = c.get('/create_user/')
        self.assertEqual(response.json()['message'], 'Incorrect request method, should be POST')
        response = c.get('/home/')
        self.assertEqual(response.json()['message'], 'Incorrect request method, should be POST')
        response = c.get('/create_hifi/')
        self.assertEqual(response.json()['message'], 'Incorrect request method, should be POST')
        response = c.get('/sent_hifi/')
        self.assertEqual(response.json()['message'], 'Incorrect request method, should be POST')
        response = c.get('/delete_hifi/')
        self.assertEqual(response.json()['message'], 'Incorrect request method, should be POST')
        response = c.get('/delete_sent_hifi/')
        self.assertEqual(response.json()['message'], 'Incorrect request method, should be POST')
        response = c.get('/block_user/')
        self.assertEqual(response.json()['message'], 'Incorrect request method, should be POST')
        response = c.get('/unblock_user/')
        self.assertEqual(response.json()['message'], 'Incorrect request method, should be POST')
        response = c.get('/report_hifi/')
        self.assertEqual(response.json()['message'], 'Incorrect request method, should be POST')
        response = c.get('/update_user_profile/')
        self.assertEqual(response.json()['message'], 'Incorrect request method, should be POST')
        response = c.post('/logout/')
        self.assertEqual(response.json()['message'], 'Incorrect request method, should be GET')
        response = c.get('/contact_sync/')
        self.assertEqual(response.json()['message'], 'Incorrect request method, should be POST')
        response = c.get('/update_user_location/')
        self.assertEqual(response.json()['message'], 'Incorrect request method, should be POST')

    def test_create_user(self):
        print('test_create_user')

        c = Client()
        digid = "b"
        name = "test name"
        phone = "9423094803"
        fp = open('media/test.jpg', 'rb')
        response = c.post('/create_user/', {'digits_id': digid, 'name': name, 'phone': phone, 'photo': fp,
                                            'email': 'anshuman@storyboard.co'})
        fp.close()
        self.assertEqual(response.status_code, 200)
        r = json.loads(response.content.decode())
        self.assertEqual(r.get('message'), "User created")
        self.assertEqual(r.get('status'), True)
        self.assertEqual(r.get('code'), 200)

        user = r.get('data')
        self.assertEqual(user.get('phone'), phone)
        self.assertEqual(user.get('digits_id'), digid)
        self.assertEqual(user.get('name'), name)
        self.assertIsNotNone(user.get('avatar'))

    def test_verify_user_success_response(self):
        print('test_verify_user_success_response')

        c = Client()
        response = c.post('/verify_user/', {'digits_id': 1})
        self.assertEqual(response.status_code, 200)
        r = json.loads(response.content.decode())
        self.assertEqual(r.get('message'), "Login successful")
        self.assertEqual(r.get('status'), True)
        self.assertEqual(r.get('code'), 200)

        user = r.get('data')
        self.assertEqual(user.get('phone'), self.user[0]['phone'])
        self.assertEqual(user.get('digits_id'), self.user[0]['digits_id'])
        self.assertEqual(user.get('userid'), self.user[0]['userid'])
        self.assertEqual(user.get('name'), self.user[0]['name'])
        self.assertIsNotNone(user.get('avatar'))
        self.assertIsNotNone(user.get('sessionid'))

    def test_verify_user_fail_response(self):
        print('test_verify_user_fail_response')
        c = Client()
        response = c.post('/verify_user/', {'digits_id': '849846465'})
        self.assertEqual(response.status_code, 400)
        r = json.loads(response.content.decode())
        self.assertEqual(r.get('message'), "User with the provided digits id not found")
        self.assertEqual(r.get('status'), False)
        self.assertEqual(r.get('code'), 400)

    def test_create_hifi_success_response(self):
        print('test_create_hifi_success_response')
        c = Client()
        # c.post('/verify_user/', {'digits_id': self.user[0]['digits_id']})
        fp = open('media/test.jpg', 'rb')
        response = c.post('/create_hifi/', {
            'lat': '28.0198', 'lng': "-82.739817", 'location': "dummy location",
            'post': 'hello all', 'hf_userids': self.user[0]['userid'], 'map_image': fp,
            'digits_id': self.user[0]['digits_id']
        })

        self.assertEqual(response.status_code, 200)
        r = json.loads(response.content.decode())
        self.assertEqual(r.get('message'), "Hifi created successfully")
        self.assertEqual(r.get('status'), True)
        self.assertEqual(r.get('code'), 200)

    def test_home_api(self):
        print('test_home_api')
        c = Client()
        response = c.post('/home/', {'digits_id': self.user[0]['digits_id']})

        self.assertEqual(response.status_code, 200)
        r = json.loads(response.content.decode())
        self.assertEqual(r.get('message'), "User's received hifis")
        self.assertEqual(r.get('status'), True)
        self.assertEqual(r.get('code'), 200)
        self.assertEqual(len(r.get('data')), 2)

    def test_report_hifi_api(self):
        print('test_report_hifi_api')

        c = Client()
        c.post('/verify_user/', {'digits_id': self.user[0]['digits_id']})
        c.post('/report_hifi/', {'hifi_id': self.post['post_id']})

        resp = json.loads(c.get('/home/').content.decode())
        hifi_id = resp.get('data')
        # desc(hifi_id)
        response = c.post('/report_hifi/', {'hifi_id': hifi_id[0]['hifi']['post_id']})
        self.assertEqual(response.status_code, 200)
        r = response.json()
        self.assertEqual(r.get('message'), "Hifi reported")
        self.assertEqual(r.get('status'), True)
        self.assertEqual(r.get('code'), 200)
        resp = json.loads(c.get('/home/').content.decode())
        hifi_id_2 = resp.get('data')
        self.assertEqual(len(hifi_id), len(hifi_id_2) + 1)

    def test_block_user_api(self):
        print('test_block_user_api')
        c = Client()
        # User 1 logs in
        c.post('/verify_user/', {'digits_id': self.user[1]['digits_id']})
        # User 1 sees his posts
        response = c.get('/home/')
        r0 = response.json()['data']

        # User 3 logs in
        c.post('/verify_user/', {'digits_id': self.user[2]['digits_id']})
        # User 2 creates hifi for user 1
        fp = open('media/test.jpg', 'rb')
        rx = c.post('/create_hifi/', {
            'lat': '28', 'lng': "82", 'location': "dummy location",
            'post': 'hello all', 'hf_userids': self.user[1]['userid']
        })
        fp.close()
        hifis = Hifireceived.objects.all()
        for h in hifis:
            h.flag = Hifireceived.FLAG_RECEIVED
            h.save()

        # User 1 logs in
        c.post('/verify_user/', {'digits_id': self.user[1]['digits_id']})

        # User 1 sees his posts
        response = c.get('/home/')
        r1 = response.json()['data']
        # User 1 blocks user 2
        response = c.post('/block_user/', {'user_id': self.user[2]['userid']})
        r = response.json()
        self.assertEqual(r['data']['hf_userid']['userid'], self.user[2]['userid'])
        self.assertEqual(r.get('message'), "User blocked")
        self.assertEqual(r.get('status'), True)
        self.assertEqual(r.get('code'), 200)

        # user 1 can't see user 2's posts in home
        response = c.get('/home/')
        r2 = response.json()['data']
        self.assertEqual(len(r1), len(r2) + 1)

    def test_unblock_user_api(self):
        print('test_unblock_user_api')
        c = Client()
        # User 1 logs in
        response = c.post('/verify_user/', {'digits_id': self.user[1]['digits_id']})
        self.assertEqual(response.json()['status'], True)

        response = c.get('/home/')
        r1 = response.json()['data']
        c.post('/block_user/', {'user_id': r1[0]['hifi']['sender']['userid']})
        response = c.get('/home/')
        r2 = response.json()['data']
        self.assertNotEqual(len(r1), len(r2))

        c.post('/unblock_user/', {'user_id': r1[0]['hifi']['sender']['userid']})
        response = c.get('/home/')
        r3 = response.json()['data']
        self.assertEqual(len(r1), len(r3))

    def test_del_sent_hifi_api(self):
        print('test_del_sent_hifi_api')
        c = Client()
        # User 3 logs in
        response = c.post('/verify_user/', {'digits_id': self.user[3]['digits_id']})
        self.assertEqual(response.json()['status'], True)
        response = c.get('/sent_hifi/')
        l1 = len(response.json()['data'])
        c.post('/delete_sent_hifi/', {'hifi_id': response.json()['data'][0]['post_id']})
        response = c.get('/sent_hifi/')
        l2 = len(response.json()['data'])
        self.assertEqual(l1, l2 + 1)

    def test_del_hifi_api(self):
        print('test_del_hifi_api')
        c = Client()

        response = c.post('/verify_user/', {'digits_id': self.user[1]['digits_id']})
        self.assertEqual(response.json()['status'], True)

        # User 1 sees his posts
        response = c.get('/home/')
        r1 = response.json()['data']
        # User 1 deletes
        response = c.post('/delete_hifi/', {'hifi_id': r1[0]['msg_id']})
        r = response.json()
        self.assertEqual(r['data']['hifi_id'], r1[0]['msg_id'])
        self.assertEqual(r.get('message'), "Hifi deleted")
        self.assertEqual(r.get('status'), True)
        self.assertEqual(r.get('code'), 200)

        # user 1 can't see user 0's posts in home
        response = c.get('/home/')
        r2 = response.json()['data']
        self.assertEqual(len(r1), len(r2) + 1)

    def test_sent_hifi_api(self):
        print('test_sent_hifi_api')

        c = Client()
        # User 0 logs in
        response = c.post('/verify_user/', {'digits_id': self.user[3]['digits_id']})
        self.assertEqual(response.json()['status'], True)

        response = c.get('/sent_hifi/')
        r = response.json()
        self.assertEqual(r['data'][0]['sender']['userid'], self.user[3]['userid'])
        self.assertEqual(r.get('message'), "User's sent hifis")
        self.assertEqual(r.get('status'), True)
        self.assertEqual(r.get('code'), 200)

    def test_contact_sync_api(self):
        print('test_contact_sync_api')

        c = Client()

        response = c.post('/verify_user/', {'digits_id': self.user[0]['digits_id']})
        self.assertEqual(response.json()['status'], True)
        response = c.post('/contact_sync/', {'contact': ','.join([self.user[i]['phone'] for i in range(3)])})
        self.assertEqual(response.json()['status'], True)
        self.assertEqual(len(response.json()['data']), 3)

    # def test_logout_api(self):
    #     c = Client()
    #
    #     response = c.post('/verify_user/', {'digits_id': self.user[0]['digits_id']})
    #     self.assertEqual(response.json()['status'], True)
    #
    #     response = c.get('/logout/')
    #     r = response.json()
    #     self.assertEqual(r.get('message'), "Successfully logged out")
    #     self.assertEqual(r.get('status'), True)
    #     self.assertEqual(r.get('code'), 200)
    #
    #     response = c.get('/home/')
    #     r = response.json()
    #     self.assertEqual(r.get('message'), "User is not logged in")
    #     self.assertEqual(r.get('status'), False)
    #     self.assertEqual(r.get('code'), 401)

    def tearDown(self):
        pass
        # mydir = os.getcwd() + '/attachments/'
        # list(map(os.unlink, (os.path.join(mydir, f) for f in os.listdir(mydir))))
        # mydir = os.getcwd() + '/profile_pics/'
        # list(map(os.unlink, (os.path.join(mydir, f) for f in os.listdir(mydir))))
