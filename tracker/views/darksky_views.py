from ..forms import AddLocationForm, CreateJournalForm, DateRecordForm, UpdateDateRecordForm, DateRecordNotesForm, UpdatePrecipRecordForm , UpdateShareForm, HomeLocationForm
from ..models import User, Location, Journal, Date_record, Precip_record, Date_record_note, Share, Current_location
from django.db.models.functions import Lower
from datetime import datetime, date, timedelta
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, render_to_response
from django.utils.html import conditional_escape as esc
from django.utils.safestring import mark_safe
from django.views import generic, View
from itertools import groupby
import json
import requests

class CurrentWeather(LoginRequiredMixin, View):

    def get(self,request):
        try:
            location = self.get_location(request)
        except:
            location = None
        if location != None:
            data = self.call_darksky(request)
            current_temp = data["weatherdata"]["currently"]["temperature"]
            location_name = data["location"]["location_name"]
            sunrise = data["weatherdata"]["daily"]["data"][0]["sunriseTime"]
            sunset = data["weatherdata"]["daily"]["data"][0]["sunsetTime"]
            daylight = self.diff_unix(sunset,sunrise)
            return render(
                request,
                'tracker/current_weather.html',
                context={'location_name':location_name, 'current_temp':current_temp, 'sunrise':self.convert_unix(sunrise), 'sunset':self.convert_unix(sunset), 'daylight':daylight })
        else:
            return redirect(HomeLocation)

    def get_location(self, request):
        try:
            location = Location.objects.get(current_location__user=request.user)
        except:
            loaction = None
        return location

    def call_darksky(self, request):
        location = self.location_details(request)
        response = requests.get('https://api.darksky.net/forecast/d021c6ab4940997d6a5440c4e72a1006/'+location['user_lat']+','+location['user_long']+'?exclude=minutely,hourly,alerts,flags')
        weatherdata = response.json()
        return ({'weatherdata':weatherdata, 'location':location})

    def location_details(self, request):
        user_location = self.get_location(request)
        user_long = user_location.longitude
        user_lat = user_location.latitude
        location_name = user_location.locality_name
        return ({'user_long':str(user_long), 'user_lat':str(user_lat), 'location_name':location_name})

    def convert_unix(self, unix_timestamp):
        converted_timestamp = datetime.fromtimestamp(unix_timestamp).strftime('%H:%M:%S')
        return converted_timestamp

    def diff_unix(self, unix_timestamp1, unix_timestamp2):
        seconds_diff = (unix_timestamp1 - unix_timestamp2)
        hours_mins_secs =  str(timedelta(seconds = seconds_diff))
        return hours_mins_secs
