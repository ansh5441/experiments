from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^edit_tags/$', views.edit_tags, name='edit_tags'),
    url(r'^send_undelivered_hifis/$', views.send_undelivered_hifis, name='send_undelivered_hifis'),
    # url(r'^temp_rename_user_avatar/$', views.temp_rename_user_avatar, name='temp_rename_user_avatar'),
    url(r'^save_subscription_email/$', views.save_subscription_email, name='save_subscription_email'),
    url(r'^save_campus_ambassador/$', views.save_campus_ambassador, name='save_campus_ambassador'),
    url(r'^location_notification/$', views.location_notification, name='location_notification'),
    url(r'^location_notification_to_user/$', views.location_notification_to_user, name='location_notification_to_user'),
    url(r'^report/$', views.report, name='report'),
    url(r'^ios_build/$', views.ios_build, name='ios_build'),
    url(r'^android_build/$', views.android_build, name='android_build'),
]
