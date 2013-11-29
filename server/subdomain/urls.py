from django.conf.urls.defaults import url, patterns, include
from django.contrib.auth.models import User, Group
import views

from django.contrib import admin
admin.autodiscover()

# Routers provide an easy way of automatically determining the URL conf

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
)
