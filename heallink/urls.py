from django.conf.urls import patterns, include, url, handler404

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'heallink.views.home', name='home'),
    # url(r'^heallink/', include('heallink.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
                           url(r'^poll/', include('poll.urls')),
                           url(r'^admin/', include(admin.site.urls)),
)

print handler404
