from django.http import HttpResponse, HttpResponseRedirect, Http404

from django.shortcuts import get_object_or_404, render
from django.template import RequestContext
from django.template.loader import get_template
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.views.defaults import permission_denied

from test_advertisement.settings import LOGIN_URL
from texts.models import TextCouple
from texts.forms import TextCoupleForm


@login_required
def add_text_couple(request):
    form = TextCoupleForm()
    user = request.user
    if request.method == 'POST':
        form = TextCoupleForm(request.POST)
        if form.is_valid():
            record_text_couple_in_db(form, user)
            return HttpResponseRedirect(reverse('texts:list_text_couples'))
    html = get_template('form.html').render(RequestContext(request, {'form': form, }))
    return HttpResponse(html)


def record_text_couple_in_db(form, user):
    short_text = form.cleaned_data['short']
    long_text = form.cleaned_data['long']
    text_couple = TextCouple(long=long_text, short=short_text, user_id=user.id)
    text_couple.save()


@login_required
def list_text_couples(request):
    text_couples = TextCouple.objects.filter(user=request.user)
    html = get_template('list_text_couples.html').render(RequestContext(request, {'text_couples': text_couples, }))
    return HttpResponse(html)


@login_required
def view_text_couple(request, text_couple_id):
    text_couple = get_object_or_404(TextCouple, pk=text_couple_id)
    if text_couple.user != request.user:
        return permission_denied(request)
    return render(request, 'texts/view_text_couple.html', {'text_couple': text_couple})


@login_required
def delete_text_couple(request, text_couple_id):
    text_couple = get_object_or_404(TextCouple, pk=text_couple_id)
    if text_couple.user != request.user:
        return permission_denied(request)
    if request.method == 'POST':
        text_couple.delete()
        return HttpResponseRedirect(reverse('texts:list_text_couples'))
    return render(request, 'texts/delete_text_couple.html', {'text_couple': text_couple})


@login_required
def change_text_couple(request, text_couple_id):
    text_couple = get_object_or_404(TextCouple, pk=text_couple_id)
    if text_couple.user != request.user:
        return permission_denied(request)
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
