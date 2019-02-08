
from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^add_location', views.AddLocation, name='add_location'),
    url(r'^home_location', views.HomeLocation, name='home_location'),
    url(r'^create_journal', views.CreateJournal, name = 'create_journal'),
    url(r'^create_date_record/(?P<pk>\d+)$', views.CreateDateRecord, name = 'create_date_record'),
    url(r'^date_record/(?P<pk>\d+)$', views.DateRecordDetailView, name = 'date_record'),
    url(r'^calendar/(?P<pk>\d+)/(?P<year>\d+)/(?P<month>\d+)$', views.calendar, name = 'calendar'),
    url(r'^update_date_record/(?P<pk>\d+)$', views.UpdateDateRecordView.as_view(), name = 'update_date_record'),
    url(r'^update_share', views.UpdateShare, name='update_share'),
    url(r'^date_range', views.GetPercipByDateRange, name='date_range'),
    url(r'^current_weather', views.CurrentWeather.as_view(), name='current_weather'),
]


