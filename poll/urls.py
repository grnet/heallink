from django.conf.urls import patterns, url

from poll import views

from django.conf import settings

urlpatterns = []

if not hasattr(settings, 'POLL_FINISHED') or settings.POLL_FINISHED == False:
    urlpatterns += patterns('',
                            url(r'cart/empty',
                                views.cart_empty,
                                name="cart_empty"),
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
    )

urlpatterns += patterns('',
                        url(r'search-journals/(?:(\d+)/(\d+)/)?$',
                            views.search_journals,
                            name="search_journals"),
                        url(r'journals/(\d+)/(\d+)/(\d+)/$',
                            views.journals_subject_area,
                            name="journals_subject_area_paged"),             
                        url(r'journals/(\d+)/$',
                            views.journals_subject_area,
                            name="journals_subject_area"),
                        url(r'journals/', views.journals, name="journals"),
                        url(r'cart/', views.cart, name="cart"),
                        url(r'cart-item/', views.cart_item, name="cart_item"),
                        url(r'user/', views.user, name="user"),
                        url(r'login/', views.login_user, name="login"),
                        url(r'logout/', views.logout_user, name="logout"),
                        url(r'first_time/', views.first_time,
                            name="first_time"),
                        url(r'help/', views.help, name="help"),
                        url('results/', views.results, name="results"),
                        url(r'^$', views.login_user),
                    )
    
