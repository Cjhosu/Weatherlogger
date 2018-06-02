from .forms import SignUpForm, AddLocationForm, CreateJournalForm, DateRecordForm, UpdateDateRecordForm, DateRecordNotesForm
from .models import User, Location, Journal, Date_record, Precip_record, Date_record_note
from calendar import HTMLCalendar, monthrange
from datetime import datetime, date
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render, render_to_response
from django.utils.html import conditional_escape as esc
from django.utils.safestring import mark_safe
from django.views import generic, View
from itertools import groupby
# Create your views here.

class IndexView(LoginRequiredMixin, View):
    def get(self, request):
        journal_list=Journal.objects.filter(user=request.user)
        return render(
            request,
            'index.html',
            context={'journal_list' :journal_list}
    )

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
    date_record_list=Date_record.objects.filter(journal_id= pk).order_by('-log_date')
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
            dr.save()

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
            ,{'form' : form, 'date_record_list':date_record_list, 'journref':journref, 'year':year, 'month':month}
            )

@login_required
def UpdateDateRecordView(request,pk):
    dateref = get_object_or_404(Date_record, pk=pk)
    try:
        prerec = get_object_or_404(Precip_record, date_record_id = pk)
    except:
        prerec = None
    try:
        noterec = get_object_or_404(Date_record_note, date_record_id = pk)
    except:
        noterec = None
    if request.method == 'POST':
        form = UpdateDateRecordForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['high_temp'] != None:
                dateref.high_temp = form.cleaned_data['high_temp']
            if form.cleaned_data['low_temp'] != None:
                dateref.low_temp = form.cleaned_data['low_temp']
            if form.cleaned_data['cloud_cover_type'] != None:
                dateref.cloud_cover_type = form.cleaned_data['cloud_cover_type']
            dateref.save()
            if prerec != None:
                if form.cleaned_data['precip_type'] != None:
                     Precip_record.objects.filter(date_record_id = pk).update(precip_type=form.cleaned_data['precip_type'])
                if form.cleaned_data['volume_in_inches'] != None:
                     Precip_record.objects.filter(date_record_id = pk).update(volume_in_inches=form.cleaned_data['volume_in_inches'])
            else:
                if form.cleaned_data['precip_type'] != None or form.cleaned_data['volume_in_inches'] != None:
                    pr = Precip_record()
                    pr.date_record_id = pk
                    pr.precip_type = form.cleaned_data['precip_type']
                    pr.volume_in_inches = form.cleaned_data['volume_in_inches']
                    pr.save()
        noteform = DateRecordNotesForm(request.POST)
        if noteform.is_valid():
            if noterec != None:
                if noteform.cleaned_data['notes'] != '':
                    Date_record_note.objects.filter(date_record_id = pk).update(note=noteform.cleaned_data['notes'])
            else:
                if noteform.cleaned_data['notes'] != '':
                    drn = Date_record_note()
                    drn.date_record_id = pk
                    drn.note = noteform.cleaned_data['notes']
                    drn.save()
            return HttpResponseRedirect('/tracker/date_record/'+ pk)
    else:
        form = UpdateDateRecordForm()
        noteform = DateRecordNotesForm()
    return render(request,
            'tracker/update_date_record.html'
            ,{'form':form, 'dateref':dateref, 'noteform':noteform}
            )

@login_required
def DateRecordDetailView(request,pk):
    daterec = get_object_or_404(Date_record, pk=pk)
    journal = get_object_or_404(Journal, pk = daterec.journal_id)
    try:
        prerec = get_object_or_404(Precip_record, date_record_id = pk)
    except:
        prerec = None
    try:
        noterec = get_object_or_404(Date_record_note , date_record_id = pk)
    except:
        noterec = None
    return render(request,
            'tracker/date_record.html',
             {'daterec' :daterec , 'prerec' :prerec, 'journal' :journal, 'noterec':noterec},
            )

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
