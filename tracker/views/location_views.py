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
