
from django.conf.urls import patterns, url

from dbtest import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
	url(r'^(?P<number>\d+)/$', views.hello),
)
