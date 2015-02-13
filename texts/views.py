from django.http import HttpResponse, HttpResponseRedirect
from texts.models import TextCouple
from texts.forms import TextCoupleForm
from django.template import RequestContext
from django.template.loader import get_template


def add_text_couple(request):
    form = TextCoupleForm()
    if request.method == 'POST':
        form = TextCoupleForm(request.POST)
        if form.is_valid():
            record_text_couple_in_db(form)
            return HttpResponseRedirect('/texts/add_text_couple/')
    html = get_template('form.html').render(RequestContext(request, {'form': form, }))
    return HttpResponse(html)


def record_text_couple_in_db(form):
    short_text = form.cleaned_data['short']
    long_text = form.cleaned_data['long']
    text_couple = TextCouple(long=long_text, short=short_text)
    text_couple.save()


def list_text_couples(request):
    amount_text_couples = TextCouple.objects.count()
    if amount_text_couples == 0:
        html = get_template('list_text_couples.html').render(RequestContext(request, {
            'content': 'No text couples were created yet', }))
    else:
        html = get_template('list_text_couples.html').render(RequestContext(request, {
            'content': 'short text long text', }))
    return HttpResponse(html)
