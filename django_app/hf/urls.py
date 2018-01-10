from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^verify_user/$', views.verify_user, name='verify_user'),
    url(r'^create_user/$', views.create_user, name='create_user'),
    url(r'^home/$', views.home, name='home'),
    url(r'^create_hifi/$', views.create_hifi, name='create_hifi'),
    url(r'^sent_hifi/$', views.sent_hifi, name='sent_hifi'),
    url(r'^delete_hifi/$', views.del_hifi, name='del_hifi'),
    url(r'^delete_sent_hifi/$', views.del_sent_hifi, name='delete_sent_hifi'),
    url(r'^block_user/$', views.block_user, name='block_user'),
    url(r'^unblock_user/$', views.unblock_user, name='unblock_user'),
    url(r'^report_hifi/$', views.report_hifi, name='report_hifi'),
    url(r'^update_user_profile/$', views.update_user_profile, name='update_user_profile'),
    url(r'^contact_sync/$', views.contact_sync, name='contact_sync'),
    url(r'^update_user_location/$', views.update_user_location, name='update_user_location'),
    url(r'^list_blocked_users/$', views.list_blocked_users, name='list_blocked_users'),
    url(r'^verify_email/$', views.verify_email, name='verify_email'),
    url(r'^view_logs/$', views.view_logs, name='view_logs'),
    url(r'^verify_api/$', views.verify_api, name='verify_api'),
    url(r'^activity/$', views.activity, name='activity'),
    url(r'^update_user_status/$', views.update_user_status, name='update_user_status'),
    url(r'^get_user_version/$', views.get_user_version, name='get_user_version'),
    url(r'^interest/$', views.interest, name='interest'),
    url(r'^interest/list/$', views.list_interests, name='list_interests'),
    url(r'^interest/subscribe/$', views.subscribe_interest, name='subscribe_interest'),
    url(r'^post/view', views.view_post, name='view_post'),
    url(r'^acknowledge_notification', views.acknowledge_notification, name='acknowledge_notification'),
    url(r'^post/like', views.like_post, name='like_post'),
    url(r'^send_chat_push', views.send_chat_push, name='send_chat_push'),
]
