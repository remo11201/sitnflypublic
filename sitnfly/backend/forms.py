from django.forms import ModelForm, DateInput, TextInput
from django.contrib.auth.forms import UserCreationForm
from .models import User
from captcha.fields import CaptchaField


class MyUserCreationForm(UserCreationForm):
    captcha = CaptchaField()
    
    class Meta:
        model = User
        fields = ['name', 'email', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = [ 'name', 'email', 'date_of_birth', 'phone_number', 'address']
        widgets = {
            'date_of_birth': DateInput(attrs={'type': 'date'}),
            'phone_number': TextInput(attrs={
                'type': 'tel',
                'pattern': r'[0-9]{8}',
                'placeholder': 'Please enter an 8 digit phone number.',
            }),
        }

