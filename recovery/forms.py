from django import forms
from flights.models import Flight


class FlightStatusForm(forms.ModelForm):
    class Meta:
        model = Flight
        fields = ['status', 'delay_minutes']
        widgets = {
            'status': forms.Select(attrs={'class': 'status-select'}),
            'delay_minutes': forms.NumberInput(attrs={'min': 0}),
        }


class RecoveryActionForm(forms.Form):
    ACTION_CHOICES = [
        ('rebook', 'Rebook'),
        ('refund', 'Refund'),
        ('voucher', 'Voucher'),
    ]
    action = forms.ChoiceField(choices=ACTION_CHOICES, widget=forms.RadioSelect)