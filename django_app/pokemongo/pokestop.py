#!/usr/bin/python
# coding=utf-8
"""Pokestop"""

import json
import math
import os
import re
import sys

import requests

DOMAIN = 'https://www.ingress.com'
COOKIES = {
    'SACSID': '<SACSID cookie>',
    'csrftoken': '<csrftoken cookie>'
}


class Pokestop(object):
    """Pokestop class"""

    def __init__(self, args={}):
        """Initializes the Pokestop class"""

        cookies = COOKIES

        if 'SACSID' in args and args['SACSID'] and 'csrftoken' in args and args['csrftoken']:
            cookies['SACSID'] = args['SACSID']
            cookies['csrftoken'] = args['csrftoken']
        else:
            try:
                with open(os.path.expanduser('~/.pokestop'), 'r') as pokefile:
                    config = json.loads(pokefile.read())

                if not config['SACSID']:
                    self.setup()
                    sys.exit(1)

                if not config['csrftoken']:
                    self.setup()
                    sys.exit(1)

                cookies['SACSID'] = config['SACSID']
                cookies['csrftoken'] = config['csrftoken']
            except IOError:
                pass

        if 'SACSID' not in cookies or not cookies['SACSID'] or cookies['SACSID'][0] == '<':
            self.setup()
            sys.exit(1)

        if 'csrftoken' not in cookies or not cookies['csrftoken'] or cookies['csrftoken'][0] == '<':
            self.setup()
            sys.exit(1)

        if 'save' in args:
            with open(os.path.expanduser('~/.pokestop'), 'w+') as pokefile:
                pokefile.write(json.dumps({
                    'SACSID': cookies['SACSID'],
                    'csrftoken': cookies['csrftoken']
                }))

        if 'latitude' in args and args['latitude']:
            cookies['ingress.intelmap.lat'] = args['latitude']

        if 'longitude' in args and args['longitude']:
            cookies['ingress.intelmap.lng'] = args['longitude']

        self.cookies = cookies
        self.headers = self.get_headers()
        self.version = self.get_version()
        self.args = args

    def setup(self):
        """Setup copy"""

        print('\033[91m')
        print('Log into %s/intel and copy the following cookies:\n  SACSID\n  csrftoken\n' % (DOMAIN))
        print('For more information, visit https://github.com/kevinselwyn/pokestop')
        print('\033[0m')

    def get_version(self):
        """Gets the version string"""

        url = '%s/intel' % (DOMAIN)
        request = requests.get(url, headers=self.headers)

        return re.findall(r'gen_dashboard_(\w*)\.js', request.text)[0]

    def get_headers(self):
        """Assembles the HTTP headers"""

        return {
            'accept-encoding': 'gzip, deflate',
            'content-type': 'application/json; charset=UTF-8',
            'cookie': "; ".join([str(x) + "=" + str(y) for x, y in self.cookies.items()]),
            'origin': DOMAIN,
            'referer': DOMAIN + '/intel',
            'user-agent': 'Mozilla/2.0 (compatible; MSIE 3.0; Windows 3.1)',
            'x-csrftoken': self.cookies['csrftoken']
        }

    def tile(self, lng, lat):
        """Generates the appropriate tile numbers"""

        rlat = math.radians(lat)
        tilecount = 32E3
        xtile = int((lng + 180.0) / 360.0 * tilecount)
        ytile = int((1.0 - math.log(math.tan(rlat) + (1 / math.cos(rlat))) / math.pi) / 2.0 * tilecount)

        return xtile, ytile

    def post(self, url, content):
        """Performs an HTTP post and returns the result"""

        content['v'] = self.version
        request = requests.post(url, data=json.dumps(content), headers=self.headers)

        return request.json()['result']

    def map(self, tilekeys):
        """Gets the map entities"""

        url = DOMAIN + '/r/getEntities'
        content = {
            'tileKeys': tilekeys
        }

        return self.post(url, content)

    def stop(self, guid):
        """Get single portal"""

        url = DOMAIN + '/r/getPortalDetails'
        content = {
            'guid': guid
        }

        return self.post(url, content)

    def distance(self, start_lat, start_lng, end_lat, end_lng):
        """Calculates the distance between two coordinates"""

        radius = 6371e3
        lat_start = math.radians(start_lat)
        lat_end = math.radians(end_lat)
        lat_diff = math.radians(end_lat - start_lat)
        lng_diff = math.radians(end_lng - start_lng)
        accumulation = (math.sin(lat_diff / 2) * math.sin(lat_diff / 2)) + (
            math.cos(lat_start) * math.cos(lat_end) * math.sin(lng_diff / 2) * math.sin(lng_diff / 2))
        result = 2 * math.atan2(math.sqrt(accumulation), math.sqrt(1 - accumulation))

        return int(math.floor(radius * result))

    def bearing(self, start_lat, start_lng, end_lat, end_lng):
        """Calculates the bearing between two coordinates"""

        y_var = math.sin(end_lng - start_lng) * math.cos(end_lat)
        x_var = (math.cos(start_lat) * math.sin(end_lat)) - (
            math.sin(start_lat) * math.cos(end_lat) * math.cos(end_lng - start_lng))

        return int(math.floor(360 - ((math.degrees(math.atan2(y_var, x_var)) + 360) % 360)))

    def compass(self, bearing):
        """Converts a degree bearing to a cardinal direction"""

        compass = 'N'

        if bearing >= 337.5 or bearing < 22.5:
            compass = 'N'
        elif bearing >= 22.5 and bearing < 67.5:
            compass = 'NE'
        elif bearing >= 67.5 and bearing < 112.5:
            compass = 'E'
        elif bearing >= 112.5 and bearing < 157.5:
            compass = 'SE'
        elif bearing >= 157.5 and bearing < 202.5:
            compass = 'S'
        elif bearing >= 202.5 and bearing < 247.5:
            compass = 'SW'
        elif bearing >= 247.5 and bearing < 292.5:
            compass = 'W'
        elif bearing >= 292.5 and bearing < 337.5:
            compass = 'NW'

        return compass

    def entities(self):
        """Collects pokestops"""

        lat = math.floor(float(self.cookies['ingress.intelmap.lat']) * 1E6) / 1E6
        lng = math.floor(float(self.cookies['ingress.intelmap.lng']) * 1E6) / 1E6
        minxtile, maxytile = self.tile(((lng * 1E6) - 100) / 1E6, ((lat * 1E6) - 100) / 1E6)
        maxxtile, minytile = self.tile(((lng * 1E6) + 100) / 1E6, ((lat * 1E6) + 100) / 1E6)
        output = []

        if 'minimum' not in self.args:
            self.args['minimum'] = 0

        if 'maximum' not in self.args:
            self.args['maximum'] = 10000

        for xtile in range(minxtile, maxxtile + 1):
            for ytile in range(minytile, maxytile + 1):
                tilekey = '15_{}_{}_8_8_25'.format(xtile, ytile)
                result = self.map([tilekey])
                entities = result['map'][tilekey]['gameEntities']

                for entity in entities:
                    guid = entity[0]

                    try:
                        latitude = entity[2][2] / 1E6
                        longitude = entity[2][3] / 1E6
                    except TypeError:
                        continue
                    #
                    # distance = self.distance(lat, lng, latitude, longitude)
                    #
                    # if distance < self.args['minimum']:
                    #     continue
                    #
                    # if distance > self.args['maximum']:
                    #     continue

                    image = entity[2][7]
                    name = entity[2][8]
                    # bearing = self.bearing(lat, lng, latitude, longitude)
                    # compass = self.compass(bearing)

                    output.append({
                        'guid': guid,
                        'latitude': latitude,
                        'longitude': longitude,
                        'image': image,
                        'name': name,
                        # 'distance': distance,
                        # 'bearing': bearing,
                        # 'compass': compass
                    })

        if 'order' not in self.args:
            self.args['order'] = 'ASC'

        if 'limit' not in self.args:
            self.args['limit'] = 10000

        if 'offset' not in self.args:
            self.args['offset'] = 0

        # output.sort(
        #     key=lambda x: x['distance'],
        #     reverse=self.args['order'] == 'DESC'
        # )

        output = output[self.args['offset']:self.args['offset'] + self.args['limit']]

        return output

    def entity(self, guid):
        """Collects single pokestop"""

        entity = self.stop(guid)

        latitude = entity[2] / 1E6
        longitude = entity[3] / 1E6
        image = entity[7]
        name = entity[8]

        distance = None
        bearing = None
        compass = None

        if 'ingress.intelmap.lat' in self.cookies and 'ingress.intelmap.lng' in self.cookies:
            lat = math.floor(float(self.cookies['ingress.intelmap.lat']) * 1E6) / 1E6
            lng = math.floor(float(self.cookies['ingress.intelmap.lng']) * 1E6) / 1E6

            distance = self.distance(lat, lng, latitude, longitude)
            bearing = self.bearing(lat, lng, latitude, longitude)
            compass = self.compass(bearing)

        output = {
            'guid': guid,
            'latitude': latitude,
            'longitude': longitude,
            'image': image,
            'name': name,
            'distance': distance,
            'bearing': bearing,
            'compass': compass
        }

        return json.dumps(output, indent=4)


def main():
    """Main function"""
    args = {"csrftoken": "KrC5dILDzSfyGYTdOuk0P7ZNanrVRNsv",
            "SACSID": """~AJKiYcG_GzhmrIH-wHeFC1QE2U540HyYy8n7WK1uwi_6jTgLzPS5UFWrfvxe1XiSfbSEoN1L6jY8BWxX7zdPM_1FVyv4jwbwqfd1FS-HcL8IhD769flzqNpWX5EmbdnWFje81MNPOW2NYRCygRd8PHBXjKMVT_O0cM5ZXy8Jg5Tm75WYJ8tKEBeIRq8UeeriC-avEbgUlRnIqw868OUY2K6NTu6V15Lz-5GSlGwGWxkPzwaXfQr6iA1oLU-tjitfp5RsRFNZM3Ai84dH-tpgxcMAZEFM5co1N69T-Mr2-jxCgzBfD9x_lH4PUty-oyjAR90Z7sS8CzSo"""}
    args['latitude'] = 12.912079
    args['longitude'] = 77.681600
    pokestop = Pokestop(args)
    print(json.dumps(pokestop.entities(), indent=4))

    # if args.guid:
    #     print(pokestop.entity(args.guid))
    # else:


if __name__ == '__main__':
    main()
