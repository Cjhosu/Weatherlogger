from ..forms import DateRangeForm, SignUpForm, AddLocationForm, CreateJournalForm, DateRecordForm, UpdateDateRecordForm, DateRecordNotesForm, UpdatePrecipRecordForm , UpdateShareForm, HomeLocationForm
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from ..models import User, Location, Journal, Date_record, Precip_record, Date_record_note, Share, Current_location
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

