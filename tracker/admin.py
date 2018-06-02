from django.contrib import admin
from .models import Location, Journal, Group, Cloud_cover_type, Precip_type, Date_record, Precip_record, Date_record_note

# Register your models here.

admin.site.register(Location)
admin.site.register(Journal)
admin.site.register(Group)
admin.site.register(Cloud_cover_type)
admin.site.register(Precip_type)
admin.site.register(Date_record)
admin.site.register(Precip_record)
admin.site.register(Date_record_note)
