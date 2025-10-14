from django import forms
from .models import Account, UserProfile
from email_validator import validate_email, EmailNotValidError

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
        
    def clean_email(self):
        email = self.cleaned_data.get('email')

        # 1. Check if inactive user exists → allow form to pass
        inactive_user = Account.objects.filter(email=email, is_active=False).first()
        if inactive_user:
            return email

        # 2. Check if active user exists → raise error
        active_user = Account.objects.filter(email=email, is_active=True).first()
        if active_user:
            raise forms.ValidationError("email already exists.")

        # 3. Validate email deliverability
        try:
            valid = validate_email(email, check_deliverability=True)
            return valid.email
        except EmailNotValidError:
            raise forms.ValidationError("Email does not exist")


class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'mobile_number']

    def __init__(self,  *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, error_messages = {'invalid':("Image files only")}, widget=forms.FileInput)
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'address_line_1', 'address_line_2', 'pin_code', 'city', 'state', 'country']

    def __init__(self,  *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
