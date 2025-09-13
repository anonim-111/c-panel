from django import forms
from dal import autocomplete

from .models import Patient


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = "__all__"
        widgets = {
            'inspector': autocomplete.ModelSelect2(
                url='inspector-autocomplete',
                forward=['neighborhood']
            ),
            'psychiatrist': autocomplete.ModelSelect2(
                url='psychiatrist-autocomplete',
                forward=['neighborhood']
            ),
        }
