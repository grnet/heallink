from django.conf.urls import patterns, url

from poll import views

urlpatterns = patterns('',
                       url(r'journals/', views.journals, name="journals"),
                       url(r'add-remove-journal/',
                           views.add_remove_journal,
                           name="add_remove_journal"),
                       url(r'cart/', views.cart, name="cart"),
                       url(r'user/', views.user, name="user"),
                       url(r'login/', views.login_user, name="login"),
                       url(r'logout/', views.logout_user, name="logout"),
                       )
