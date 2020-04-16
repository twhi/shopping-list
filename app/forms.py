from django import forms
from django.contrib.auth.forms import UserCreationForm
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
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(max_length=254)

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