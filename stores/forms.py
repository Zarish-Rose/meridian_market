from django import forms

from .models import Store, StoreMember


class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = [
            'name',
            'description',
            'website',
        ]


class StoreMemberForm(forms.ModelForm):
    class Meta:
        model = StoreMember
        fields = ['user', 'role']

