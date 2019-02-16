from ..forms import DateRangeForm, AddLocationForm, CreateJournalForm, DateRecordForm, UpdateDateRecordForm, DateRecordNotesForm, UpdatePrecipRecordForm , UpdateShareForm, HomeLocationForm
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
