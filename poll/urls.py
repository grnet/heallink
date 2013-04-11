from django.conf.urls import patterns, url

from poll import views

urlpatterns = patterns('',
                       url(r'journals/', views.journals, name="journals"),
                       url(r'cart/', views.cart, name="cart"),
                       url(r'cart-item/', views.cart_item, name="cart_item"),
                       url(r'user/', views.user, name="user"),
                       url(r'login/', views.login_user, name="login"),
                       url(r'logout/', views.logout_user, name="logout"),
                       )
