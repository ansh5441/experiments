import logging

from django.conf import settings
from django.db import models

logger = logging.getLogger(__name__)


class Img(models.Model):
    pic = models.FileField(null=True, upload_to='tag_images')
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(null=True)

    def __str__(self):
        return self.pic.name


class Typ(models.Model):
    txt = models.CharField(max_length=128, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(null=True)

    def __str__(self):
        return self.txt


class Tag(models.Model):
    txt = models.CharField(max_length=128, null=True)
    pic = models.ForeignKey(Img)
    typ = models.ForeignKey(Typ)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(null=True)

    def get_dic(self):
        if self.pic.pic.name != '' and self.pic.pic.name is not None:
            pic = settings.AWS_S3_CUSTOM_DOMAIN + '/' + str(self.pic.pic.name)

        dic = {
            'txt': self.txt,
            'pic': pic,
            'type': self.typ.txt
        }
        return dic

    def __str__(self):
        return self.txt


class SubscriptionEmail(models.Model):
    email = models.CharField(max_length=128, null=True)
    created_at = models.DateTimeField(null=True)


class CampusAmbassador(models.Model):
    first_name = models.CharField(max_length=128, null=True)
    last_name = models.CharField(max_length=128, null=True)
    email = models.CharField(max_length=128, null=True)
    university = models.CharField(max_length=128, null=True)
    major = models.CharField(max_length=64, null=True)
    phone = models.CharField(max_length=15, null=True)
    fb = models.CharField(max_length=128, null=True)
    country = models.CharField(max_length=128, null=True)
    how_popular = models.CharField(max_length=256, null=True)
    referral = models.CharField(max_length=25, null=True)
    created_at = models.DateTimeField(null=True)
