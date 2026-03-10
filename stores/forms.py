from django import forms
from .models import Store, StoreMember

class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = [
            'name',
            'description',
            'website',
            'logo',
            'tagline',
            'primary_color',
            'accent_color',
        ]
        
class StoreMemberForm(forms.ModelForm):
    class Meta:
        model = StoreMember
        fields = ['user', 'role']
        