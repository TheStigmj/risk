from django.conf.urls import url

from . import views

app_name = 'userprofile'
urlpatterns = [
	# ex: /risk/5/results/
	#url('<int:question_id>/results/', views.results, name='results'),
	# ex: /risk/5/
	#url('<int:question_id>/', views.detail, name='detail'),
	# ex: /risk/
	#url(r'^(?P<pk>\d+)/$', views.DetailView.as_view(), name='detail'),
	#url(r'^(?P<pk>\d+)/edit$', views.CustomerEdit.as_view(), name='edit'),
	#url(r'^(?P<pk>\d+)/$', views.CustomerDetail.as_view(), name='detail'),
	url(r'^$', views.UserprofileIndex.as_view(), name='index'),
	url(r'^(?P<number>\d+)/$', views.UserprofileDetail.as_view(), name='detail'),
	url(r'^(?P<number>\d+)/edit/$', views.UserprofileUpdateView.as_view(), name='edit'),
	#url(r'^(?P<content_type_id>\d+)/add/(?P<obj_id>\d+)/$', views.WatchlistAdd, name='add'),
	#url(r'^(?P<content_type_id>\d+)/remove/(?P<obj_id>\d+)/$', views.WatchlistRemove, name='remove'),
]