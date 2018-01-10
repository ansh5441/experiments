from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^campaign/create/$', views.create_campaign, name='create_campaign'),
    url(r'^campaign/view/', views.view_campaign, name='view_campaign')
]
