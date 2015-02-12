from django import forms


class TextCoupleForm(forms.Form):
    short = forms.CharField(label='Enter title, make it short', max_length=30, min_length=3)
    long = forms.CharField(label='Enter description', max_length=140, widget=forms.Textarea)
