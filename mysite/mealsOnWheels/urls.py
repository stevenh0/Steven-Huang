## To create URLconf in teh polls directory, createa file called urls.py.
from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^$',views.index,name='index'),
    url(r'^specifics/(?P<question_id>[0-9]+)/$',views.detail,name='detail'),
    url(r'^(?P<question_id>[0-9]+)/results/$',views.results,name='results'),
    url(r'^(?P<question_id>[0-9]+)/vote/$',views.vote,name='vote'),
    url(r'^register/$',views.register_user,name='register'),
    url(r'^confirm/(?P<activation_key>\w+)$',views.register_confirm,name='register_confirm'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$',views.user_logout,name='logout'),
    url(r'^map/$',views.render_map,name='map'),
    url(r'^food_truck/$',views.render_json,name='food_truck'),
    ]
