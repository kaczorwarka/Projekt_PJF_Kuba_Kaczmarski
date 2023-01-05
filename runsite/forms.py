from django import forms
from datetime import datetime


class DateInput(forms.DateInput):
    input_type = 'date'


class getData(forms.Form):
    city = forms.CharField(required=False, label="City", max_length=200,
                           widget=forms.TextInput(attrs={'class': 'bg-secondary border-0 text-white fs-6',
                                                         'style': '--bs-bg-opacity: .0;', 'id': 'Input'}))
    date_from = forms.DateField(required=False, label="Date",
                                widget=DateInput(attrs={'class': 'bg-secondary border-0 text-white fs-6',
                                                        'style': '--bs-bg-opacity: .0;', 'id': 'Input2'}))
    date_to = forms.DateField(required=False, label="Date",
                              widget=DateInput(attrs={'class': 'bg-secondary border-0 text-white fs-6',
                                                      'style': '--bs-bg-opacity: .0;'}))
    distance_from = forms.DecimalField(required=False, min_value=0,
                                       widget=forms.NumberInput(attrs={'class': 'bg-secondary border-0 text-white fs-6',
                                                                       'style': '--bs-bg-opacity: .0;', 'id': 'Input3'}))
    distance_to = forms.DecimalField(required=False, min_value=0,
                                     widget=forms.NumberInput(attrs={'class': 'bg-secondary border-0 text-white fs-6',
                                                                     'style': '--bs-bg-opacity: .0;', 'id': 'Input3'}))


class getTraningInfo(forms.Form):
    # Choices = [()]
    CHOICE = (("Basic", "Basic"), ("Medium", "Medium"), ("Advance", "Advance"))
    # type = forms.CharField(label="Traning type", widget=forms.RadioSelect(choices=CHOICE))
    type = forms.CharField(label="Traning type", widget=forms.Select(choices=CHOICE,
                                                                     attrs={'class': 'form-select '}))
    time_hours = forms.CharField(required=False, label="Hours",
                                 widget=forms.TextInput(attrs={'placeholder': '2h', 'class': 'form-control'}))
    time_minutes = forms.CharField(required=False, label="Minutes",
                                   widget=forms.TextInput(attrs={'placeholder': '30min', 'class': 'form-control'}))
