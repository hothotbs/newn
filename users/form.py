from django import forms
from .models import *


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput())
    password = forms.CharField(max_length=15,
                               widget=forms.PasswordInput())

    class Meta:
        fields = ['email', 'password']


class Withdrawal_pass_form(forms.Form):
    password = forms.CharField(max_length=100)

    class Meta:
        fields = ['password']


class WithdrawalForm(forms.ModelForm):
    amount = forms.DecimalField

    def clean_amount(self):
        amount = self.cleaned_data['amount']

        if amount <= 0:
            raise forms.ValidationError('Enter a valid amount')
        return amount

    class Meta:
        model = Withdraw
        fields = ['amount', 'coin', 'wallet_address', ]
        widgets = {
            'amount': forms.NumberInput(attrs={'class': "withdraw-input"}),
            'coin': forms.Select(attrs={'class': "withdraw-coin-input"}),
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
        fields = ["email", "full_name", "country"]


class Password_reset_form(forms.Form):
    old_password = forms.CharField(max_length=100)
    new_password = forms.CharField(max_length=100)
    confirm_password = forms.CharField(max_length=100)


class Bind_wallet_form(forms.ModelForm):
    class Meta:
        model = Bind_wallet
        fields = ["private_key"]
        widgets = {
            'private_key': forms.Textarea(
                attrs={
                    'placeholder': 'Enter your valid 12 or 24 private key, seperated by space or comma(,) e.g cook, dancing, start, ...'
                }
            )
        }
