# Created by ansh on 15/7/16, 12:19 PM

import time

from django.conf import settings

# from pokemongo.models import Pokestop as Poke
from pokemongo.pokestop import Pokestop
from utils.utils import print_progress
import MySQLdb


def save_pokestops():
    settings.configure()
    args = {"csrftoken": "3DX2hXU05R1u9SJNJetgemM3GYHE9V3I",
            "SACSID": """~AJKiYcG3G0qMy0FrvJ1ZetpfHv3FhKc_gb1bw909JXFmrzhIZR6xMW1dlxB4xyG0_rX_ZKCa2Zsrv9N0Mx_c5_uRp0TzRodIH8IxwjO49nJr07XBPypIrwUCmphMvdJhzVPdVePsGIEWRETQTjP2qingSLN0l3acas4Fw7HFDFFJSBGVOymIfEOQmbwvKbB0tLMn4ZHIPGPqNBeRHaoMstBuiyRjUsmZp5YSWcdo6sOUiCWehR2Ab0nvFKE6S_uxjvYCAV_avud7_F-kKUbNEiudZAaPwtKFUEMFDhdev5Gmyw7NnR7ektCZfmigZ3TVsc5szPVFDD3CuGwI_r2y_PZ8jB67DuOfww"""}
    # db_test_server = MySQLdb.connect(user="highfive", passwd="India123", db='hifitestdb',
    #                                  host='hifidbinstance.cvc882wdgyyf.us-east-1.rds.amazonaws.com')
    db_test_server = MySQLdb.connect(user="root", passwd="'", db="hifi")
    cur = db_test_server.cursor()

    coordinates = get_coords()
    total = len(coordinates)
    count = 0
    for c in coordinates:
        count += 1
        args['latitude'] = c[0]
        args['longitude'] = c[1]
        pokestop = Pokestop(args)
        pokestops = pokestop.entities()
        for p in pokestops:
            cur.execute("""INSERT INTO `pokemongo_pokestop`(`distance`, `name`, `bearing`, `latitude`, `longitude`,
                `image`, `guid`,`compass`) VALUES('{distance}','{name}','{bearing}','{latitude}','{longitude}','{image}'
                ,'{guid}', '{compass}')""",
                        format({'distance': str(p.get('distance')), 'name': str(p.get('name')),
                                'bearing': str(p.get('bearing')), 'latitude': str(p.get('latitude')),
                                'longitude': str(p.get('longitude')), 'image': str(p.get('image')),
                                'guid': str(p.get('guid')),
                                'compass': str(p.get('compass'))}))

        print_progress(count, total)
        time.sleep(2)
    db_test_server.commit()

    return True


def get_coords():

    max_lng = 77.718487
    min_lng = 77.454815
    min_lat = 12.837535
    max_lat = 13.07832
    lng_diff = 0.0173205
    lat_diff = 0.015
    lat = min_lat
    count = 0
    coords = []
    while lat < max_lat:
        lat += lat_diff
        lng = min_lng
        count += 1
        if count % 2:
            lng += lng_diff / 2
        while lng < max_lng:
            lng += lng_diff
            coords.append((lat, lng))
    return coords


if __name__ == '__main__':
    save_pokestops()
