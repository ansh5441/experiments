import random
import time

import requests

from utils import print_progress


def create_fake_users(url):
    print("Creating Users")
    names = ['Jennifer', 'Scarlett', 'Tom', 'Jason', 'Ben']
    for i in range(5):
        u_dic = {
            'digits_id': i + 1,
            'name': names[i],
            'phone': i + 1,
            'email': 'anshuman@storyboard.co',
        }
        pic = {'photo': open('./files/u' + str(i + 1) + '.jpg', 'rb')}
        requests.post(url + 'create_user/', u_dic, files=pic)
        print_progress(i + 1, 5)


def create_fake_posts(url):
    print("Creating Posts")
    dic = {1: [(3,), (3, 4)],
           2: [(3,), (3, 1)],
           3: [(3,), (3,), (3,), (1,), (2,), (5,), (1, 2, 5), (4, 5)],
           4: [(3,), (3, 2)],
           5: [(3,), (3, 1)]
           }

    count = 0
    z = get_post_string()
    for k in dic.keys():
        # requests.post(url + 'verify_user/', {'digits_id': k})
        ar = dic[k]
        pic_num = 1
        for a in ar:
            to_users = ','.join(['HF' + str(x) for x in a])
            # for userid in a:
            #     to_users += 'HF' + str(userid)
            post = {
                'lat': 1,
                'lng': 1,
                'location': 'New York',
                'post': next(z),
                'hf_userids': to_users,
                'condition': 0,
                'digits_id': k
            }
            if random.random() < 0.5 and pic_num <= 8:
                pic = {'attachment': open('./files/p' + str(pic_num) + '.jpg', 'rb')}
                pic_num += 1
                requests.post(url + 'create_hifi/', post, files=pic)
            else:
                requests.post(url + 'create_hifi/', post)
            count += 1
            print_progress(count, 16)


def get_post_string():
    f = open('rand_txt.txt', 'r')
    y = f.readlines()
    t = [line for line in y]
    txt = ' '.join(t)
    length = len(txt)
    pos = 0
    while pos < length:
        post_len = random.randint(50, 200)
        end = pos + post_len
        yield (txt[pos:end])
        pos = end
    f.close()


if __name__ == "__main__":
    url = 'http://54.87.134.135/'
    url = 'http://127.0.0.1:8000/'
    # create_fake_users(url)
    create_fake_posts(url)
    # i = 0
    # t1 = time.time()
    # while i < 100:
    #     i += 1
    #     requests.post(url + 'update_user_location/', {'digits_id': 732067161573752832, 'lat': 78, 'lng': 24})
    #     print_progress(i, 100)
    # t2 = time.time()
    # print((t2 - t1) / 100)
