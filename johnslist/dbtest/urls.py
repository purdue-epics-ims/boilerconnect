from django.conf.urls import patterns, url

from dbtest import views

urlpatterns = patterns('',
	url(r'^user/(?P<user_id>[0-9]+)$', views.user_detail,name='user_detail'),
	url(r'^organization/(?P<organization_id>[0-9]+)$', views.organization_detail,name='organization_detail'),
	url(r'^job/(?P<job_id>[0-9]+)$', views.job_detail,name='job_detail'),
	url(r'^organization/(?P<organization_id>[0-9]+)/jobs$', views.organization_job_index,name='organization_job_index'),
	)
