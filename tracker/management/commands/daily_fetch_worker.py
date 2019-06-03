from django.conf import settings
from django.core.management.base import BaseCommand
from ...views.darksky_views import CurrentWeather
from ...models import Darksky_historical_data, Location
import requests
from datetime import date, datetime, timedelta

darkskykey = settings.DARK_SKY_KEY
yesterday = datetime.now() - timedelta(days=1)
yest = yesterday.strftime('%s')

class Command(BaseCommand):

    url = 'https://api.darksky.net/forecast/'+darkskykey+'/'
    help = "Fetches weatherdate for a location on a schedule."

    def add_arguments(self, parser):
        parser.add_argument('--location')

    def getHistoricalData(self,provided_location):
        home_location = Location.objects.get(locality_name = provided_location)
        latitude = str(home_location.latitude)
        longitude = str(home_location.longitude)
        response = requests.get(self.url+latitude+','+longitude+','+yest+'?exclude=minutely,currently,hourly,alerts,flags')
        weatherdata = response.json()
        uv_index = weatherdata["daily"]["data"][0]["uvIndex"]
        return ({'uv_index':uv_index, 'home_location': home_location})

    def handle(self,*args, **options):
        provided_location = options['location']
        historical_data = self.getHistoricalData(provided_location)
        max_uv_index = historical_data["uv_index"]
        location_key = historical_data["home_location"]
        data = Darksky_historical_data()
        data.max_uv_index = max_uv_index
        data.log_date = yesterday.date()
        data.location = location_key
        data.save()
