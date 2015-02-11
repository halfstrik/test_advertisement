from django.http import HttpResponseRedirect
from django.shortcuts import render

from texts.forms import TextCoupleForm
from texts.models import TextCouple


def add_text_couple(request):
    if request.method == 'POST':
        form = TextCoupleForm(request.POST)
        if form.is_valid():
            short_cleaned = form.cleaned_data['short']
            long_cleaned = form.cleaned_data['long']
            TextCouple.objects.create(long=long_cleaned, short=short_cleaned)
            return HttpResponseRedirect('/')
    else:
        form = TextCoupleForm()
    return render(request, 'texts/add_text_couple.html', {'form': form})
