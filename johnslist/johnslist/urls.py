from django.conf.urls import include, url
from django.contrib import admin
from johnslist import settings
from dbtest import urls
# import notifications
# url('^inbox/notifications/', include(notifications.urls)),

urlpatterns = [
	url(r'^admin/', include(admin.site.urls),name='admin'),
	url(r'^', include(urls),name='base'),
]
if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns.append(
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT})
    )
