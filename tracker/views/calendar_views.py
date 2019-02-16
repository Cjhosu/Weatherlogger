from ..forms import DateRangeForm, SignUpForm, AddLocationForm, CreateJournalForm, DateRecordForm, UpdateDateRecordForm, DateRecordNotesForm, UpdatePrecipRecordForm , UpdateShareForm, HomeLocationForm
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from ..models import User, Location, Journal, Date_record, Precip_record, Date_record_note, Share, Current_location
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
