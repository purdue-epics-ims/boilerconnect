from django.conf.urls import patterns, url
from django.contrib.auth.views import logout
from dbtest import views

urlpatterns = patterns('',
    #user urls
    url(r'^user/?$', views.user_dash,name='user_dash'),
    url(r'^user/create/?$', views.user_create,name='user_create'),
    url(r'^user/(?P<user_id>[0-9]+)/user_job_index/?$', views.user_job_index,name='user_job_index'),
    url(r'^user/(?P<user_id>[0-9]+)/user_membership/?$', views.user_membership,name='user_membership'),
    url(r'^user/edit/?$', views.user_edit,name='user_edit'),
    #organization urls
    url(r'^organization/(?P<organization_id>[0-9]+)/dash/?$', views.organization_dash,name='organization_dash'),
    url(r'^organization/(?P<organization_id>[0-9]+)/?$', views.organization_detail,name='organization_detail'),
    url(r'^organization/(?P<organization_id>[0-9]+)/jobs/?$', views.organization_job_index,name='organization_job_index'),
    url(r'^organization/(?P<organization_id>[0-9]+)/accept/?$', views.organization_accept_job,name='organization_accept_job'),
    url(r'^organization/create/?$', views.organization_create,name='organization_create'),
    url(r'^organization/(?P<organization_id>[0-9]+)/edit/?$', views.organization_edit,name='organization_edit'),
    #job urls
    url(r'^job/(?P<job_id>[0-9]+)/?$', views.job_dash,name='job_dash'),
    url(r'^job/create/?$', views.job_create,name='job_create'),
    url(r'^organization/(?P<organization_id>[0-9]+)/job/(?P<job_id>[0-9]+)/?$', views.jobrequest_dash,name='jobrequest_dash'),
    #misc urls
    url(r'^$',views.front_page,name='front_page'),
	url(r'^search/?$',views.search,name='search'),
    url(r'^login/?$', views.login,name='login'),
	url(r'^logout/?$', logout,{'template_name':'dbtest/logout.html'},name='logout'),
    url(r'^about/?$', views.about, name='about'),
    url(r'^notifications/?$', views.notifications, name='notifications'),
 )


