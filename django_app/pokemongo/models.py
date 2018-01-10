from django.db import models


class Pokestop(models.Model):
    name = models.CharField(max_length=128, null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    image = models.CharField(max_length=256, null=True)
    guid = models.CharField(max_length=64, primary_key=True)