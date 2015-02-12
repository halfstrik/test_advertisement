from django import forms


class TextCoupleForm(forms.Form):
    short = forms.CharField(label='Enter title, make it short', min_length=3, max_length=30)
    long = forms.CharField(label='Enter description', max_length=140)
