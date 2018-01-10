from django.db import models


class User(models.Model):
    name = models.CharField(max_length=255, null=True)
    avatar = models.FileField(null=True, upload_to='profile_pics')
    email = models.CharField(max_length=256, default=None, null=True)
    password = models.CharField(max_length=512, null=True, default=0)
    updated = models.DateTimeField(null=True)
    created = models.DateTimeField(null=True)


class Business(models.Model):
    name = models.CharField(max_length=255, null=True)
    user = models.ForeignKey(User)
    sub_category = models.ForeignKey(Sub_category)
    updated = models.DateTimeField(null=True)
    created = models.DateTimeField(null=True)


class Category(models.Model):
    name = models.CharField(max_length=255, null=True)
    updated = models.DateTimeField(null=True)
    created = models.DateTimeField(null=True)


class Sub_category(models.Model):
    name = models.CharField(max_length=255, null=True)
    category = models.ForeignKey(Category)
    updated = models.DateTimeField(null=True)
    created = models.DateTimeField(null=True)


class Interest(models.Model):
    name = models.CharField(max_length=255, null=True)
    sub_category = models.ForeignKey(Sub_category)
    updated = models.DateTimeField(null=True)
    created = models.DateTimeField(null=True)


class Store(models.Model):
    name = models.CharField(max_length=255, null=True)
    address = models.CharField(max_length=255, null=True)
    latitude = models.CharField(max_length=64, null=True)
    longitude = models.CharField(max_length=64, null=True)
    image = models.FileField(max_length=255, null=True)
    updated = models.DateTimeField(null=True)
    created = models.DateTimeField(null=True)


class Campaign(models.Model):
    business = models.ForeignKey(Business)
    campaign_type = models.ForeignKey(Campaign_type)
    name = models.CharField(max_length=255, null=True)
    budget = models.CharField(max_length=255, null=True)
    messages_sent = models.CharField(max_length=10, null=True)
    daily_cap = models.CharField(max_length=255, null=True)
    proximity = models.CharField(max_length=255, null=True)
    image = models.FileField(null=True)
    start_dt = models.DateTimeField(null=True)
    end_dt = models.DateTimeField(null=True)
    repeat = models.CharField(max_length=10, null=True)
    updated = models.DateTimeField(null=True)
    created = models.DateTimeField(null=True)


class Message(models.Model):
    text = models.CharField(max_length=2048, null=True)
    campaign = models.ForeignKey(Campaign)
    updated = models.DateTimeField(null=True)
    created = models.DateTimeField(null=True)


class Option(models.Model):
    text = models.CharField(max_length=2048, null=True)
    message = models.ForeignKey(Message)
    updated = models.DateTimeField(null=True)
    created = models.DateTimeField(null=True)


class Campaign_type(models.Model):
    name = models.CharField(max_length=128, null=True)
    updated = models.DateTimeField(null=True)
    created = models.DateTimeField(null=True)


class Billing(models.Model):
    updated = models.DateTimeField(null=True)
    created = models.DateTimeField(null=True)


class Payement(models.Model):
    data = models.CharField(max_length=64, null=True)
    business = models.ForeignKey(Business)
    updated = models.DateTimeField(null=True)
    created = models.DateTimeField(null=True)
