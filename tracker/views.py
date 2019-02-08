from .forms import DateRangeForm, SignUpForm, AddLocationForm, CreateJournalForm, DateRecordForm, UpdateDateRecordForm, DateRecordNotesForm, UpdatePrecipRecordForm , UpdateShareForm, HomeLocationForm
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from .models import User, Location, Journal, Date_record, Precip_record, Date_record_note, Share, Current_location
from calendar import HTMLCalendar, monthrange
from django.db.models.functions import Lower
from datetime import datetime, date, timedelta
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render, render_to_response
from django.utils.html import conditional_escape as esc
from django.utils.safestring import mark_safe
from django.views import generic, View
from itertools import groupby
import json
import requests
# Create your views here.

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            adduser = User.objects.get(username=username)
            adduser.email = form.cleaned_data['email']
            adduser.first_name = form.cleaned_data['first_name']
            adduser.last_name = form.cleaned_data['last_name']
            adduser.save()
            login(request, user)
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

class IndexView(LoginRequiredMixin, View):
    def get(self, request):
        journal_list=Journal.objects.filter(user=request.user)
        shared_list = Journal.objects.filter(share__shared_with_user=request.user)
        return render(
            request,
            'index.html',
            context={'journal_list' :journal_list , 'shared_list' :shared_list, }
    )

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

@login_required
def HomeLocation(request):
    if request.method == 'POST':
      form = HomeLocationForm(request.POST)
      if form.is_valid():
          user = request.user
          location = form.cleaned_data.get('location')
          obj, created = Current_location.objects.update_or_create(
                  user = user,
                  defaults = { 'location':location }
                  )
          return HttpResponseRedirect('/tracker/current_weather')
      else:
          return HttpResposnseRedirect('/tracker/')
    else:
        form = HomeLocationForm()
    return render(request, 'tracker/home_location.html', {'form' : form})

@login_required
def AddLocation(request):
    if request.method == 'POST':
      form = AddLocationForm(request.POST)
      if form.is_valid():
          LocMod = Location()
          LocMod.locality_name = form.cleaned_data.get('locality_name')
          LocMod.zip = form.cleaned_data.get('zip')
          LocMod.save()
          return HttpResponseRedirect('/tracker/')
      else:
          return HttpResposnseRedirect('/tracker/')
    else:
        form = AddLocationForm()
    return render(request, 'tracker/add_location.html', {'form' : form})

@login_required
def CreateJournal(request):
    if request.method == 'POST':
      form = CreateJournalForm(request.POST)
      if form.is_valid():
          JourMod = Journal()
          JourMod.user = request.user
          JourMod.locality = form.cleaned_data.get('locality')
          JourMod.description = form.cleaned_data.get('description')
          JourMod.save()
          return HttpResponseRedirect('/tracker/')
      else:
          return HttpResposnseRedirect('/tracker/')
    else:
        form = CreateJournalForm()
    return render(request, 'tracker/create_journal.html', {'form' : form})

@login_required
def CreateDateRecord(request,pk):
    journref = get_object_or_404(Journal, pk=pk)
    userref = journref.user
    date_record_list = Date_record.objects.filter(journal_id= pk).order_by('-log_date')
    paginator = Paginator(date_record_list, 15)
    page = request.GET.get('page')
    records = paginator.get_page(page)
    now = datetime.now()
    year = now.year
    month = now.month
    if request.method == 'POST':
        form = DateRecordForm(request.POST)
        if form.is_valid():
            dr = Date_record()
            dr.log_date = form.cleaned_data['log_date']
            dr.journal_id = journref.pk
            dr.high_temp = form.cleaned_data['high_temp']
            dr.low_temp = form.cleaned_data['low_temp']
            dr.cloud_cover_type = form.cleaned_data['cloud_cover_type']
            try:
                dr.save()
            except:
                    dupe = 'there is a record for that date already'
                    return render(request,
                    'tracker/create_date_record.html'
                    ,{'form' : form, 'records':records,'dupe' : dupe, 'journref':journref, 'year':year, 'month':month}
                    )
            pr = Precip_record()
            pr.date_record_id = dr.id
            pr.precip_type = form.cleaned_data['precip_type']
            pr.volume_in_inches = form.cleaned_data['volume_in_inches']
            if pr.precip_type != None:
                pr.save()

            drn = Date_record_note()
            drn.date_record_id = dr.id
            drn.note = form.cleaned_data['notes']
            if drn.note != '':
                drn.save()

            return HttpResponseRedirect('/tracker/create_date_record/'+ pk)
    else:
        form = DateRecordForm()
    return render(request,
            'tracker/create_date_record.html'
            ,{'form' : form, 'records':records, 'journref':journref, 'userref':userref, 'year':year, 'month':month}
            )

@login_required
def DateRecordDetailView(request,pk):
    daterec = get_object_or_404(Date_record, pk=pk)
    journal = get_object_or_404(Journal, pk = daterec.journal_id)
    if is_precip_record(request, pk) == True:
        prerec = Precip_record.objects.get(date_record_id = pk)
    else:
        prerec = None
    if is_note_record(request, pk) == True:
        noterec = Date_record_note.objects.get(date_record_id = pk)
    else:
        noterec = None
    return render(request,
            'tracker/date_record.html',
             {'daterec' :daterec , 'prerec' :prerec, 'journal' :journal, 'noterec':noterec},
            )

def is_precip_record(request, pk):
    try:
        prerec = get_object_or_404(Precip_record , date_record_id = pk)
    except:
        prerec = None
    if prerec != None:
        return True

def is_note_record(request, pk):
    try:
        noterec = get_object_or_404(Date_record_note , date_record_id = pk)
    except:
        noterec = None
    if noterec != None:
        return True

class UpdateDateRecordView(LoginRequiredMixin, View):
    def get(self, request, pk):
        dateinst = get_object_or_404(Date_record, pk=pk)
        form = UpdateDateRecordForm(instance=dateinst)
        if is_precip_record(request, pk) != True:
            precipform = UpdatePrecipRecordForm()
        else:
            prerec = get_object_or_404(Precip_record , date_record_id=pk)
            precipform = UpdatePrecipRecordForm(initial={'precip_type': prerec.precip_type, 'volume_in_inches':prerec.volume_in_inches})
        if is_note_record(request, pk) != True:
            noteform = DateRecordNotesForm()
        else:
            noterec = get_object_or_404(Date_record_note, date_record_id=pk)
            noteform = DateRecordNotesForm(initial={'notes':noterec.note})
        return render(request,'tracker/update_date_record.html' ,{'form':form,'precipform':precipform, 'noteform':noteform,'dateinst':dateinst, 'pk':pk })

    def post(self, request, pk):
        dateinst = get_object_or_404(Date_record, pk=pk)
        form = UpdateDateRecordForm(request.POST, instance=dateinst)
        precipform = UpdatePrecipRecordForm(request.POST)
        noteform = DateRecordNotesForm(request.POST)
        if form.is_valid() and precipform.is_valid() and noteform.is_valid():
            if precipform.cleaned_data['precip_type'] != None:
                precip_type = precipform.cleaned_data['precip_type']
                volume_in_inches = precipform.cleaned_data['volume_in_inches']
                UpdatePrecipRecord(self,request, pk, precip_type, volume_in_inches)
            if  is_note_record(request, pk) == True or noteform.cleaned_data['notes'] != '':
                note = noteform.data['notes']
                UpdateNoteRecord(self,request,pk,note)
            form.save()
            return HttpResponseRedirect('/tracker/date_record/'+ pk)

def UpdatePrecipRecord(self, request, pk, precip_type, volume_in_inches):
    obj, created = Precip_record.objects.update_or_create(
        date_record_id = pk,
        defaults = {
        'precip_type':precip_type,
        'volume_in_inches':volume_in_inches
        })

def UpdateNoteRecord(slef, request, pk, note):
    obj, crVeated = Date_record_note.objects.update_or_create(
        date_record_id = pk,
        defaults = {
        'note':note
        })

@login_required
def UpdateShare(request):
    if request.method == 'POST':
      form = UpdateShareForm(request.user.id, request.POST)
      if form.is_valid():
          share = Share()
          journalid = form.cleaned_data['journal']
          sharedid = form.cleaned_data['user']
          share.journal = Journal.objects.get(pk=journalid)
          share.shared_with_user = User.objects.get(pk=sharedid)
          try:
              share.save()
          except:
              dupe = 'you are already sharing that journal with that user'
              return render(request, 'tracker/update_share.html', {'form' : form , 'dupe' :dupe})
          return HttpResponseRedirect('/tracker/')
      else:
          return HttpResposnseRedirect('/tracker/')
    else:
        form = UpdateShareForm(request.user.id)
    return render(request, 'tracker/update_share.html', {'form' : form ,})

@login_required
def GetPercipByDateRange(request):
    if request.method == 'POST':
        form = DateRangeForm(request.user.id, request.POST)
        if form.is_valid():
            sd = form.cleaned_data['start_date']
            ed = form.cleaned_data['end_date']
            journ = form.cleaned_data['journal']
            precip_sum = Precip_record.objects.filter(date_record__log_date__range = [sd,ed], date_record__journal = journ).values('precip_type__description').annotate(Sum('volume_in_inches'))
            return render(request, 'tracker/date_range.html', {'form':form, 'precip_sum':precip_sum})
    else:
        form = DateRangeForm(request.user.id)
    return render(request,'tracker/date_range.html', {'form':form})

class WeatherCalendar(LoginRequiredMixin,HTMLCalendar):
    def __init__(self, weather):
        super(WeatherCalendar, self).__init__()
        self.weather = self.group_by_day(weather)

    def formatday(self, day, weekday):
        if day != 0:
            cssclass = self.cssclasses[weekday]
            if date.today() == date(self.year, self.month, day):
                cssclass += ' today'
            if day in self.weather:
                cssclass += ' filled'
                body = ['<ul>']
                for weather in self.weather[day]:
                    body.append('<strong><a href="/tracker/date_record/'+esc(weather.pk)+'">')
                    try:
                        prerec = Precip_record.objects.get(date_record=weather)
                    except:
                        prerec = None
                    body.append('High Temp: ')
                    body.append(esc(weather.high_temp))
                    body.append('<br>')
                    body.append('Low Temp: ')
                    body.append(esc(weather.low_temp))
                    body.append('<br>')
                    body.append(esc(weather.cloud_cover_type))
                    body.append('<br>')
                    if prerec != None:
                        if prerec.volume_in_inches == None:
                            body.append('Some ')
                            body.append(esc(prerec.precip_type))
                        else:
                            body.append(esc(prerec.volume_in_inches)+ ' Inches of ')
                            body.append(esc(prerec.precip_type))
                    body.append('</a></li></strong>')
                    if  prerec == None and (str(weather.cloud_cover_type) == 'Sunny' or str(weather.cloud_cover_type) == 'Mostly Sunny'):
                        cssclass = ' nice'
                return self.day_cell(cssclass, '%d %s' % (day, ''.join(body)))
            return self.day_cell(cssclass, day)
        return self.day_cell('noday', '&nbsp;')

    def formatmonth(self, year, month):
        self.year, self.month = year, month
        return super(WeatherCalendar, self).formatmonth(year, month)

    def group_by_day(self, weather):
        field = lambda weather: weather.log_date.day
        return dict(
            [(day, list(items)) for day, items in groupby(weather, field)]
        )

    def day_cell(self, cssclass, body):
        return '<td class="%s">%s</td>' % (cssclass, body)

@login_required
def calendar(request, year, month,pk):
    year = int(year)
    month = int(month)
    journref = get_object_or_404(Journal, pk=pk)
    my_weather = Date_record.objects.order_by('log_date').filter(log_date__year=year, log_date__month=month,journal_id=pk )
    cal = WeatherCalendar(my_weather).formatmonth(year, month)
    lPreviousYear = year
    lPreviousMonth = month - 1
    if lPreviousMonth == 0:
        lPreviousMonth = 12
        lPreviousYear = year - 1
    lNextYear = year
    lNextMonth = month + 1
    if lNextMonth == 13:
        lNextMonth = 1
        lNextYear = year + 1
    lYearAfterThis = year + 1
    lYearBeforeThis = year - 1
    return render_to_response('tracker/calendar.html', {'calendar': mark_safe(cal),'PreviousMonth' : lPreviousMonth,
                                                       'PreviousYear' : lPreviousYear,
                                                       'NextMonth' : lNextMonth,
                                                       'NextYear' : lNextYear,
                                                       'YearBeforeThis' : lYearBeforeThis,
                                                       'YearAfterThis' : lYearAfterThis,
                                                       'journref' : journref,
                                                   })
