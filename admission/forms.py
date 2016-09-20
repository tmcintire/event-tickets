from django import forms
from models import *


class AdmissionForm(forms.ModelForm):
    class Meta:
        model = AdmissionType
        fields = ('event', 'type', 'price')


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expenses
        fields = ('name', 'type', 'category', 'notes', 'percent', 'cost')

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ('event', 'type', 'notes', 'amount')
