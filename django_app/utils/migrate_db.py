import os.path
import urllib.request

import MySQLdb
import requests

# from . import clean_db as cl
# from utils import desc
import sys

import time

from utils import print_progress
# from utils.utils import print_progress
from clean_db import clean_local_tables, clean_remote_test_tables


def save_all_file_names():
    print('Saving file names from server to local file')
    url = 'http://hifibucket.s3.amazonaws.com/'
    resp = requests.get(url)
    f = open('files.txt', 'w')
    r = resp.content.decode()
    f.write(r)


def get_all_file_names():
    print('Getting file names from local file')
    f = open('files.txt', 'r')
    y = f.readline()
    count = 0
    names = []
    while y != '':
        count += 1
        y = f.readline()
        start = 0
        loc = 1

        while loc != -1:
            loc = y.find('<Key>', start)
            loc2 = y.find('</Key>', start)
            name = y[loc:loc2]
            names.append(name)
            names[-1] = names[-1][5:]
            start = loc2 + 1
    return names


def save_all_files(url, names):
    tot = len(names)
    count = 1
    suc_cnt = 0
    fail_cnt = 0
    fails = []
    for n in names:
        count += 1
        fname = 'migfiles/' + n
        if os.path.isfile(fname) is False:
            try:
                urllib.request.urlretrieve(url + n, fname)
            except Exception as e:

                fail_cnt += 1
                fails.append(n)
            else:
                suc_cnt += 1
                print_progress(suc_cnt, tot)
        else:
            suc_cnt += 1
            print_progress(suc_cnt, tot)
    print('\n' + str(len(fails)) + ' failures ')
    [print(f) for f in fails]


def create_users(url):
    print("Creating Users")
    db = MySQLdb.connect(user="root", passwd="'", db="mig_hf")
    c = db.cursor()
    c.execute("""SELECT * FROM hf_users""")
    res = c.fetchall()
    users = []
    for r in res:
        u_dic = {
            'id': r[0],
            'digits_id': r[1],
            'userid': r[2],
            'name': r[3],
            'avatar': r[5].split('/')[-1],
            'phone': r[7],
            'email': r[4],
        }
        users.append(u_dic)

    fails = []
    total = len(users)
    count = 0
    for u in users:
        try:
            pic = {'photo': open('./migfiles/' + u['avatar'], 'rb')}
        except:
            pic = {}
        del (u['avatar'])
        resp = requests.post(url + 'create_user/', u, files=pic)
        if resp.status_code != 200:
            fails.append((u, resp.content.decode()))

        else:
            count += 1
            print_progress(count, total)

    print('\n' + str(len(fails)) + ' failures ')
    [print(f) for f in fails]


def create_posts(url='http://127.0.0.1:8000/'):
    print("Creating Posts")
    db = MySQLdb.connect(user="root", passwd="'", db="mig_hf")
    c = db.cursor()
    c.execute("SELECT * FROM hf_hifipost p JOIN hf_users u ON p.userid = u.userid")
    res = c.fetchall()
    count = 0
    total = len(res)
    fails = []
    for p in res:
        post_dic = {
            'lat': str(p[6]),
            'lng': str(p[7]),
            'location': p[5],
            'post': p[4],
            'hf_userids': p[3],
            'digits_id': p[16]
        }
        pic = {}
        try:
            pic['attachment'] = open('./migfiles/' + p[1] + '.jpg', 'rb')
        except:
            pass

        try:
            pic['map_image'] = open('./migfiles/' + "M" + p[1] + '.jpg', 'rb')
        except:
            pass

        # print(p[1])
        requests.post(url + 'verify_user/', {'digits_id': p[16]})
        resp = requests.post(url + 'create_hifi/', post_dic, files=pic)
        if resp.status_code != 200:
            fails.append((post_dic, resp.content.decode()))
        else:
            count += 1
            print_progress(count, total)

    print('\n' + str(len(fails)) + ' failures ')
    [print(f) for f in fails]


def create_locations(url='http://127.0.0.1:8000/'):
    print("Creating Locations")
    db = MySQLdb.connect(user="root", passwd="'", db="mig_hf")
    c = db.cursor()
    c.execute("""SELECT * FROM hf_location l JOIN hf_users u ON l.userid = u.userid""")
    res = c.fetchall()
    count = 0
    fail_count = 0
    total = len(res)
    fails = []
    for r in res:
        s = requests.Session()
        post_dict = {'lat': r[2], 'lng': r[3], 'digits_id': r[6]}
        resp = s.post(url + 'update_user_location/', post_dict)
        if resp.status_code != 200:
            fail_count += 1
            fails.append((post_dict, resp.content.decode()))
        else:
            count += 1
            print_progress(count, total)
    print('\n' + str(fail_count) + ' failures ')
    [print(f) for f in fails]


def print_dict(d):
    for di in d.keys():
        print(str(di) + ": " + str(d[di]))
        print()


if __name__ == '__main__':
    # clean_remote_test_tables()
    # url = 'http://54.87.134.135/'
    clean_local_tables()
    url = 'http://54.208.101.63/'
    url = 'http://127.0.0.1:8000/'
    save_all_file_names()
    save_all_files('http://hifibucket.s3.amazonaws.com/', get_all_file_names())

    create_users(url)
    create_posts(url)
    create_locations(url)
    # update hifiproddb.hf_hifireceived, highfivetestdb.hf_hifipost set hifiproddb.hf_hifireceived.updated_at = highfivetestdb.hf_hifipost.updated_at where hifiproddb.hf_hifireceived.post_id = REPLACE(highfivetestdb.hf_hifipost.postid,'PO','');
    # url = "http://127.0.0.1:8000/"
    # resp = requests.post(url+'verify_user/',{'digits_id':1})

    # print_dict(resp.headers)


    # create_locations()
    # [[print(k, p[k]) for k in p.keys()] for p in u]
    # names = get_all_file_names()
    #
    # url = 'http://hifibucket.s3.amazonaws.com/'
    # fails = save_all_files(url, names)
    # while len(fails) > 4:
    #     fails = save_all_files(url, names)
