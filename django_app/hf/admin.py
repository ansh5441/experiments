from django.contrib import admin

from .models import Users, Hifipost, Location, Hifireceived, Block, Friend, Interest, InterestData, UserInterest

admin.site.register(Users)
admin.site.register(Hifipost)
admin.site.register(Hifireceived)
admin.site.register(Location)
admin.site.register(Block)
admin.site.register(Friend)
admin.site.register(Interest)
admin.site.register(InterestData)
admin.site.register(UserInterest)
