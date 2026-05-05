from django import forms
from .models import *
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField(max_length=15, )
    password = forms.CharField(max_length=15,
                               widget=forms.PasswordInput())

    class Meta:
        fields = ['username', 'password']


class WithdrawalForm(forms.ModelForm):
    amount = forms.DecimalField

    def clean_amount(self):
        amount = self.cleaned_data['amount']

        if amount <= 0:
            raise forms.ValidationError('Enter a valid amount')
        return amount

    class Meta:
        model = Withdraw
        fields = ['amount', 'wallet_address']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': "withdraw-input"})
        }


class DepositForm(forms.ModelForm):

    def clean_amount(self):
        amount = self.cleaned_data['amount']

        if amount <= 0:
            raise forms.ValidationError('Enter a valid amount')
        return amount

    class Meta:
        model = Deposit
        fields = ['amount', 'image', 'mode_of_payment']
        labels = {
            'image': 'Upload Proof Of Payment'
        }
        widgets = {
            'amount': forms.NumberInput(attrs={'class': "withdraw-input"})
        }


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]
