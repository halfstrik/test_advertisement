from django.http import HttpResponse, HttpResponseRedirect

from django.shortcuts import get_object_or_404, render
from django.template import RequestContext
from django.template.loader import get_template
from django.core.urlresolvers import reverse

from texts.models import TextCouple
from texts.forms import TextCoupleForm


def add_text_couple(request):
    form = TextCoupleForm()
    if request.method == 'POST':
        form = TextCoupleForm(request.POST)
        if form.is_valid():
            record_text_couple_in_db(form)
            return HttpResponseRedirect(reverse('texts:list_text_couples'))
    html = get_template('form.html').render(RequestContext(request, {'form': form, }))
    return HttpResponse(html)


def record_text_couple_in_db(form):
    short_text = form.cleaned_data['short']
    long_text = form.cleaned_data['long']
    text_couple = TextCouple(long=long_text, short=short_text)
    text_couple.save()


def list_text_couples(request):
    text_couples = TextCouple.objects.all()
    html = get_template('list_text_couples.html').render(RequestContext(request, {'text_couples': text_couples, }))
    return HttpResponse(html)


def view_text_couple(request, text_couple_id):
    text_couple = get_object_or_404(TextCouple, pk=text_couple_id)
    return render(request, 'texts/view_text_couple.html', {'text_couple': text_couple})


def delete_text_couple(request, text_couple_id):
    text_couple = get_object_or_404(TextCouple, pk=text_couple_id)
    if request.method == 'POST':
        text_couple.delete()
        return HttpResponseRedirect(reverse('texts:list_text_couples'))
    return render(request, 'texts/delete_text_couple.html', {'text_couple': text_couple})


def change_text_couple(request, text_couple_id):
    text_couple = get_object_or_404(TextCouple, pk=text_couple_id)
    form = TextCoupleForm()
    if request.method == 'POST':
        form = TextCoupleForm(request.POST)
        if form.is_valid():
            short_text = form.cleaned_data['short']
            long_text = form.cleaned_data['long']
            text_couple.short = short_text
            text_couple.long = long_text
            text_couple.save()
            return HttpResponseRedirect(reverse('texts:list_text_couples'))
    return render(request, 'texts/change_text_couple.html', {'form': form, 'text_couple': text_couple})
