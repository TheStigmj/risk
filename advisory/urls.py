from django.conf.urls import url

from . import views

app_name = 'advisory'
urlpatterns = [
	# ex: /risk/5/results/
	#url('<int:question_id>/results/', views.results, name='results'),
	# ex: /risk/5/
	#url('<int:question_id>/', views.detail, name='detail'),
	# ex: /risk/
	url(r'^(?P<pk>\d+)/edit$', views.DetailUpdateView.as_view(), name='edit'),
	url(r'^(?P<pk>\d+)/$', views.DetailView.as_view(), name='detail'),
	url(r'^add$', views.DetailAddView.as_view(), name='add'),
	url(r'^$', views.IndexView.as_view(), name='index'),
]