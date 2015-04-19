from django.conf.urls import patterns, url
from django.contrib.auth.views import logout
from dbtest import views

urlpatterns = patterns('',
	url(r'^user/(?P<user_id>-?[0-9]+)/?$', views.user_detail,name='user_detail'),
	url(r'^organization/(?P<organization_id>[0-9]+)/?$', views.organization_detail,name='organization_detail'),
	url(r'^organization/(?P<organization_id>[0-9]+)/jobs/?$', views.organization_job_index,name='organization_job_index'),
	url(r'^organization/(?P<organization_id>[0-9]+)/accept/?$', views.organization_accept_job,name='organization_accept_job'),
	url(r'^organization/create/?$', views.organization_create,name='organization_create'),
	url(r'^job/create/?$', views.job_create,name='job_create'),
	url(r'^job/(?P<job_id>[0-9]+)/?$', views.job_detail,name='job_detail'),
	url(r'^user/create/?$', views.user_create,name='user_create'),
	url(r'^$',views.front_page,name='front_page'),
	url(r'^search/?$',views.search,name='search'),
	url(r'^user/(?P<user_id>[0-9]+)/user_job_index/?$', views.user_job_index,name='user_job_index'),
	url(r'^user/(?P<user_id>[0-9]+)/user_membership/?$', views.user_membership,name='user_membership'),
	url(r'^login/?$', views.login,name='login'),
	url(r'^logout/?$', logout,{'template_name':'dbtest/logout.html'},name='logout'),
	url(r'^user/edit/?$', views.user_edit,name='user_edit'),
    url(r'^organization/edit/?$', views.organization_edit,name='organization_edit'),
	url(r'^about/?$', views.about, name='about'),
 )
      
