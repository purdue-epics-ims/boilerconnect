<<<<<<< HEAD
=======

>>>>>>> 224604af926632df8d37a7badb2b12cfb7e4d45b
from django.conf.urls import patterns, url

from dbtest import views

urlpatterns = patterns('',
	url(r'^organizations$', views.organization_index),
	url(r'^jobs$', views.job_index),
	url(r'^users$', views.user_index),
	)
>>>>>>> 224604af926632df8d37a7badb2b12cfb7e4d45b
