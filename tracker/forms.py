from django import forms
from django.forms import ModelForm
from .models import Location, Journal, Date_record, Cloud_cover_type, Precip_type, Date_record_note, User
from django.contrib.auth.forms import UserCreationForm

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None

class AddLocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = '__all__'

class CreateJournalForm(forms.ModelForm):
    class Meta:
        model = Journal
        fields = ('description','locality')

class DateInput(forms.DateInput):
    input_type = 'date'

class DateRecordForm(forms.Form):
    log_date = forms.DateField(widget = DateInput())
    cloud_cover_type = forms.ModelChoiceField(queryset=Cloud_cover_type.objects.all())
    high_temp = forms.IntegerField()
    low_temp = forms.IntegerField()
    precip_type = forms.ModelChoiceField(queryset=Precip_type.objects.all(), required = False)
    volume_in_inches = forms.FloatField(required = False)
    notes = forms.CharField(widget=forms.Textarea, required = False)

class UpdateDateRecordForm(forms.ModelForm):
    high_temp = forms.IntegerField(required = False)
    low_temp = forms.IntegerField(required = False)
    cloud_cover_type = forms.ModelChoiceField(queryset=Cloud_cover_type.objects.all(), required = False)
    class Meta:
        model = Date_record
        fields = ('high_temp', 'low_temp', 'cloud_cover_type')

class UpdatePrecipRecordForm(forms.Form):
    precip_type = forms.ModelChoiceField(queryset=Precip_type.objects.all(), required = False)
    volume_in_inches = forms.FloatField(required = False)

class DateRecordNotesForm(forms.Form):
    notes = forms.CharField(widget=forms.Textarea, required = False)

class UpdateShareForm(forms.Form):
    journal = forms.ChoiceField(choices = [ ])
    user = forms.ChoiceField(choices = [ ])
    def __init__(self, uid, *args, **kwargs):
        super().__init__(*args, **kwargs)
        journ_choices = [ ]
        user_choices = [ ]
        for user_options in User.objects.exclude(id=uid):
            user_choices.append((user_options.id , user_options.username))
        self.fields['user'].choices = user_choices
        for journ_options in Journal.objects.filter(user_id=uid):
            journ_choices.append((journ_options.id , journ_options.description))
        self.fields['journal'].choices = journ_choices
