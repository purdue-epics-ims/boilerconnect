from django.conf.urls import patterns, url

from dbtest import views

urlpatterns = patterns('',
    url(r'^organizations$', views.organization_index),
    url(r'^jobs$', views.job_index),
    url(r'^users$', views.user_index),
	)
