from django import forms
from .models import Account

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email', 'mobile_number', 'password']

    def __init__(self,  *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        # self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'   // If you want to add placeholder then this is the way.
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    
    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data['password']
        confirm_password = cleaned_data['confirm_password']

        if password != confirm_password:
            raise forms.ValidationError("password does not match!!")