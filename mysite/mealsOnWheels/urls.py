## To create URLconf in teh polls directory, createa file called urls.py.
from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^$',views.index,name='index'),
    url(r'^register/$',views.register_user,name='register'),
    url(r'^confirm/(?P<activation_key>\w+)$',views.register_confirm,name='register_confirm'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$',views.user_logout,name='logout'),
    url(r'^map/$',views.render_map,name='map'),
    url(r'^filterVendor/$',views.filterVendor ,name='filterVendor'),
    url(r'^food_trucks/$',views.render_json,name='food_trucks'),
    url(r'^profile/$', views.change_profile_settings, name='profile'),
    url(r'^about/$', views.render_about, name='about'),
    ]
