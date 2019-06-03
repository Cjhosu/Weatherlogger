import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
# Create your models here.

class Location(models.Model):
    locality_name = models.CharField(max_length=255)
    zip = models.CharField(max_length=5)
    longitude = models.FloatField(null=True)
    latitude = models.FloatField(null=True)
    def __str__(self):
      return self.locality_name

class Current_location(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    def __str__(self):
      return self.location

class Journal(models.Model):
    description = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    locality = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    def __str__(self):
      return self.description

class Darksky_historical_data(models.Model):
    log_date = models.DateField(default=None, blank=True, null=True)
    max_uv_index = models.IntegerField(default=None, blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)

class Share(models.Model):
    shared_with_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    journal = models.ForeignKey(Journal, on_delete=models.SET_NULL, null=True)
    def __str__(self):
      return self.description
    class Meta:
        unique_together =('shared_with_user', 'journal')

class Cloud_cover_type(models.Model):
    description = models.CharField(max_length=25)
    def __str__(self):
      return self.description

class Precip_type(models.Model):
    description = models.CharField(max_length=10)
    def __str__(self):
      return self.description

class Date_record(models.Model):
    log_date = models.DateField(default=None, blank=True, null=True)
    cloud_cover_type = models.ForeignKey(Cloud_cover_type, on_delete=models.SET_NULL, null=True)
    high_temp = models.IntegerField(default=None, blank=True, null=True)
    low_temp = models.IntegerField(default=None, blank=True, null=True)
    journal = models.ForeignKey(Journal, on_delete=models.SET_NULL, null=True)
    def __str__(self):
      return str(self.log_date)
    class Meta:
        unique_together = ('log_date' , 'journal')

class Precip_record(models.Model):
    date_record = models.ForeignKey(Date_record, on_delete=models.SET_NULL, null=True)
    precip_type = models.ForeignKey(Precip_type, on_delete=models.SET_NULL, null=True)
    volume_in_inches = models.FloatField(default=None, blank=True, null=True)
    def __str__(self):
      return str(self.volume_in_inches)

class Date_record_note(models.Model):
    date_record = models.ForeignKey(Date_record, on_delete=models.SET_NULL, null=True)
    note = models.CharField(max_length=500)
    def __str__(self):
        return str(self.note)
