from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
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
    return HttpResponse('%s %s' % (text_couple.short, text_couple.long) +
                        '<a href="%s">Delete text couple</a>'
                        % reverse('texts:del_text_couple', args=[text_couple_id]) +
                        '<a href="%s">Change text couple</a>'
                        % reverse('texts:change_text_couple', args=[text_couple_id]))


def delete_text_couple(request, text_couple_id):
    TextCouple.objects.get(pk=text_couple_id).delete()
    return HttpResponseRedirect(reverse('texts:list_text_couples'))


def change_text_couple(request, text_couple_id):
    form = TextCoupleForm(request.POST)
    form.is_valid()
    short_text = form.cleaned_data['short']
    long_text = form.cleaned_data['long']
    text_couple = TextCouple.objects.get(pk=text_couple_id)
    text_couple.short = short_text
    text_couple.long = long_text
    text_couple.save()
    return HttpResponseRedirect(reverse('texts:list_text_couples'))
