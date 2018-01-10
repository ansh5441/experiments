import time

from django.http import HttpResponse

from pokemongo.models import Pokestop as Poke
from pokemongo.pokestop import Pokestop
from utils.utils import print_progress


def get_pokestops(request):
    # return HttpResponse("")
    args = {"csrftoken": "KrC5dILDzSfyGYTdOuk0P7ZNanrVRNsv",
            "SACSID": """~AJKiYcG_GzhmrIH-wHeFC1QE2U540HyYy8n7WK1uwi_6jTgLzPS5UFWrfvxe1XiSfbSEoN1L6jY8BWxX7zdPM_1FVyv4jwbwqfd1FS-HcL8IhD769flzqNpWX5EmbdnWFje81MNPOW2NYRCygRd8PHBXjKMVT_O0cM5ZXy8Jg5Tm75WYJ8tKEBeIRq8UeeriC-avEbgUlRnIqw868OUY2K6NTu6V15Lz-5GSlGwGWxkPzwaXfQr6iA1oLU-tjitfp5RsRFNZM3Ai84dH-tpgxcMAZEFM5co1N69T-Mr2-jxCgzBfD9x_lH4PUty-oyjAR90Z7sS8CzSo"""}

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
            q = Poke()
            q.guid = p.get('guid')
            q.latitude = p.get('latitude')
            q.longitude = p.get('longitude')
            q.image = p.get('image')
            q.name = p.get('name')
            q.save()
        print_progress(count, total)
        time.sleep(1)

    return HttpResponse('success')


def get_coords():
    min_lng = -118.667208
    max_lng = -118.093173
    min_lat = 33.698590
    max_lat = 34.341689
    lng_diff = 1.73205 / 93
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
