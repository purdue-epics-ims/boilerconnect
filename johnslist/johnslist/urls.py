from django.conf.urls import patterns, include, url
from django.contrib import admin
from johnslist import settings

urlpatterns = patterns('',

	url(r'^admin/', include(admin.site.urls)),
	url(r'^', include('dbtest.urls')),
)
if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))
