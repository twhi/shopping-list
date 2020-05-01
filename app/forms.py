from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

class NewItemForm(forms.Form):
    item = forms.CharField(max_length=256, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Item',
            'id': 'new-item',
        }
    ))
    quantity = forms.IntegerField(min_value=0, widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'id': 'quantity'
        }
    ))

class InviteUserForm(forms.Form):
    email_address = forms.EmailField(max_length=256, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Email Address',
            'id': 'email-address',
        }
    ))

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254,
        widget= forms.TextInput(attrs={
            'id': 'reg-email',
            'class':'form-control',
            'placeholder': 'Email'
            })
        )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'id': 'reg-pass-1',
            'class': 'form-control',
            'placeholder':'Password'
            })
        )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'id': 'reg-pass-2',
            'class': 'form-control',
            'placeholder':'Password Confirmation'
            })
        )
    
    first_name = forms.CharField(max_length=30, required=False, 
        widget= forms.TextInput(attrs={
            'id': 'reg-first-name',
            'class':'form-control',
            'placeholder': 'First name (optional)'
            })
        )
    last_name = forms.CharField(max_length=30, required=False, 
        widget= forms.TextInput(attrs={
            'id': 'reg-last-name',
            'class':'form-control',
            'placeholder': 'Last name (optional)'
            })
        )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2', )

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
            raise forms.ValidationError('Email already in use.')
        except User.DoesNotExist:
            return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password2'])
        user.email = self.cleaned_data['email']
        user.is_active = True
        if commit:
            user.save()
        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget= forms.TextInput(attrs={
            'id': 'login-user',
            'class':'form-control',
            'placeholder': 'Email'
            })
        )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'id': 'login-pass',
            'class': 'form-control',
            'placeholder':'Password'
            })
        )