import MySQLdb
import requests
import sys

from utils import print_progress


def clean_local_tables():
    db = MySQLdb.connect(user="root", passwd="'", db="hifi")
    del_tables(db)


def clean_local_test_tables():
    db = MySQLdb.connect(user="root", passwd="'", db="hifi")
    del_tables(db)


def clean_remote_test_tables():
    db = MySQLdb.connect(user="highfive", passwd="India123", db='hifitestdb',
                         host='hifidbinstance.cvc882wdgyyf.us-east-1.rds.amazonaws.com')
    del_tables(db)


def del_tables(db):
    a = ['hf_userinterest','hf_block', 'hf_friend', 'hf_location', 'hf_hifireceived', 'hf_hifipost', 'django_session', 'django_admin_log',
         'hf_users', 'auth_user']
    clear_table(db, a)
    db.commit()


def clear_table(db, name_arr=[]):
    print('Cleaning Tables')
    c = db.cursor()
    total = len(name_arr)
    count = 0
    for n in name_arr:
        count += 1
        c.execute("DELETE FROM " + n)
        c.execute("ALTER TABLE " + n + " AUTO_INCREMENT = 1")
        print_progress(count, total)
    db.commit()


def del_test_remote_db():
    db = MySQLdb.connect(user="highfive", passwd="India123", db='hifitestdb',
                         host='hifidbinstance.cvc882wdgyyf.us-east-1.rds.amazonaws.com')
    c = db.cursor()
    c.execute("""DROP DATABASE IF EXISTS hifitestdb""")
    c.execute("""CREATE DATABASE hifitestdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci""")
    db.commit()


def del_local_db():
    db = MySQLdb.connect(user="root", passwd="'", db="hifi")
    c = db.cursor()
    c.execute("""DROP DATABASE IF EXISTS hifi""")
    c.execute("""CREATE DATABASE hifi""")
    db.commit()


def default_posts(db):
    c = db.cursor()
    # c.execute("""INSERT INTO `auth_user` (`username`,`password`,`is_superuser`,`first_name`,`last_name`,`email`,
    # `is_staff`,`is_active`,`date_joined`) VALUES ('HF1','hifi',0,'hifi','hifi','hifi',0,1,now())""")
    # c.execute("""INSERT INTO `hf_users` (`userid`,`digitsid`, `version`, `user_id`) VALUES ('HF1', 0, 0, 1)""")
    # db.commit()
    c.execute("""INSERT INTO `hf_hifipost`(`post`, `location`, `lat`, `lng`, `map_image`, `flag`,
    `sender_id`,`userid`) VALUES('Welcome to Hifi! Hifi can be a location triggered message,a reminder, a task, a scavenger hunt
    and much more. In simple, use your creativity! We are curious to see Hifi in your hands.', '50 W 4th St, New York,
     NY 10012, USA', '40.729522', ' -73.996552', 'MPO2.jpg', '1', 1,'')""")

    c.execute("""INSERT INTO `hf_hifipost`(`post`, `location`, `lat`, `lng`, `attachment`, `map_image`, `flag`,
        `sender_id`,`userid`) VALUES('Swipe Right to view Hifi on a map or just tap on the map. Swipe Left to delete, report or
         block a user.', '35-51 W 4th St, New York, NY 10012, USA', '40.729522', '-73.996552',
        'PO1.jpg', 'MPO1.jpg', '1', 1,'')""")
    db.commit()


def ejab():
    from pyejabberd import EjabberdAPIClient

    # client = EjabberdAPIClient(host='192.168.1.7', port=5222, username='admin', password='qwer1234',
    #                            user_domain='jos-macbook-air',
    #                            protocol='http', verbose=True)
    client = EjabberdAPIClient(host='localhost', port=5222, username='admin', password='admin',
                               user_domain='ex',
                               protocol='http', verbose=True)

    registered_users = client.registered_users('localhost')
    print(registered_users)
    # client.register(user='alice', host='localhost', password='@l1cepwd')


def ejab_man():
    resp = requests.post("http://localhost:5222/api/register", {
        "user": "aaaaa",
        "host": "localhost",
        "password": "ccccc"
    })

    print(resp)


def run_query(db, query):
    c = db.cursor()
    c.execute(query)
    db.commit()
    return c.fetchall()


if __name__ == '__main__':
    clean_local_tables()
    sys.exit(0)

    # db_test_server = MySQLdb.connect(user="highfive", passwd="India123", db='hifitestdb',
    #                                  host='hifidbinstance.cvc882wdgyyf.us-east-1.rds.amazonaws.com')
    # q = """INSERT INTO `hf_interestdata`(`name`, `lat`, `lng`, `image`, `guid`,`interest_id`,`message`)
    # SELECT `name`, `latitude`, `longitude`, `image`, `guid`, 1, "" FROM `pokemongo_pokestop`"""
    #
    # q = """UPDATE `hf_interestdata` SET `message`= CONCAT("Pokestop " , `name` , " is nearby")"""
    # c = db_test_server.cursor()
    # c.execute(q)
    # db_test_server.commit()
    # del_test_remote_db()
    # sys.exit(0)
    # del_local_db()
    # del_test_remote_db()
    # sys.exit()

    # ejab()
    # db_local = MySQLdb.connect(user="root", passwd="'", db="hifi")
    # q = "show tables"
    # q = "SELECT * FROM utils_subscriptionemail"
    q = "SELECT count(*) FROM pokemongo_pokestop"
    q = "SELECT * FROM hf_userinterestnotification as n join hf_interestdata as i on i.id = n.interest_data_id"
    q = "SELECT * FROM hf_hifireceived as r JOIN hf_hifipost AS p on p.id=r.post_id WHERE r.id = 6042"
    q = "SELECT * FROM hf_hifipost order by id"
    q = "UPDATE `hf_hifireceived` SET `flag`='0' WHERE id = 6065"
    q = "SELECT * FROM hf_hifireceived order by id"
    q = "SELECT * FROM hf_users"

    # clear_table(db_test_server,['utils_subscriptionemail'])
    # q = "DELETE FROM `hf_hifipost` WHERE `hf_userid` IS NULL;"

    # q = "delete from utils_campusambassador WHERE id > 7"
    # q = "ALTER TABLE utils_campusambassador AUTO_INCREMENT = 1"
    # run_query(db1, q)
    [print(p) for p in run_query(db_test_server, q)]

    # [print(a) for a in x]
    # print(run_query(db_test_server, q))

    # del_tables(db1)
    # del_dbs(db2)
    # default_posts(db2)

    # del_tables(db1)
    # default_posts(db1)
    # default_posts(db1)
    # edit_names(db1)
    # del_dbs(db1)
    # default_posts(db1)

# cd hifi_api;python3 manage.py createsuperuser
