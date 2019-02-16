from ..forms import AddLocationForm, HomeLocationForm
from ..models import User, Location, Current_location
from datetime import datetime
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, render_to_response
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
