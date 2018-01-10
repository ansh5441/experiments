# Created by ansh on 14/7/16, 5:20 PM

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^get_pokestops/$', views.get_pokestops, name='get_pokestops')
]

