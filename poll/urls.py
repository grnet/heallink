from django.conf.urls import patterns, url

from poll import views

urlpatterns = patterns('',
                       url(r'journals/', views.journals, name="journals"),
                       url(r'cart/', views.cart, name="cart"),
                       url(r'cart-item/(.+)/top',
                           views.cart_item_top,
                           name="cart_item_top"),
                       url(r'cart-item/(.+)/up',
                           views.cart_item_up,
                           name="cart_item_up"),
                       url(r'cart-item/(.+)/down',
                           views.cart_item_down,
                           name="cart_item_down"),
                       url(r'cart-item/(.+)/bottom',
                           views.cart_item_bottom,
                           name="cart_item_bottom"),
                       url(r'cart-item/(.+)/delete',
                           views.cart_item_delete,
                           name="cart_item_delete"),
                       url(r'cart-item/', views.cart_item, name="cart_item"),
                       url(r'user/', views.user, name="user"),
                       url(r'login/', views.login_user, name="login"),
                       url(r'logout/', views.logout_user, name="logout"),
                       )
