from django.http import HttpResponse, HttpResponseRedirect

from django.shortcuts import get_object_or_404, render
from django.template import RequestContext
from django.template.loader import get_template
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.views.defaults import permission_denied

from texts.models import TextCouple, TextCoupleCopy
from texts.forms import TextCoupleForm
from moderation.views import get_user_group


@login_required
def add_text_couple(request):
    form = TextCoupleForm()
    user = request.user
    if request.method == 'POST':
        form = TextCoupleForm(request.POST)
        if form.is_valid():
            record_text_couple_in_db(form, user)
            return HttpResponseRedirect(reverse('texts:list_text_couples'))
    html = get_template('texts/add_text_couple.html').render(RequestContext(request, {'form': form,
                                                                                      'user': request.user,
                                                                                      'groups': get_user_group(request.
                                                                                                               user)}))
    return HttpResponse(html)


def record_text_couple_in_db(form, user):
    short_text = form.cleaned_data['short']
    long_text = form.cleaned_data['long']
    text_couple = TextCouple(long=long_text, short=short_text, user_id=user.id)
    text_couple.save()


@login_required
def list_text_couples(request):
    text_couples = TextCouple.objects.filter(user=request.user)
    html = get_template('texts/list_text_couples.html').render(RequestContext(request,
                                                                              {'text_couples': text_couples,
                                                                               'user': request.user,
                                                                               'groups': get_user_group(request.user)}))
    return HttpResponse(html)


@login_required
def view_text_couple(request, text_couple_id):
    text_couple = get_object_or_404(TextCouple, pk=text_couple_id)
    if text_couple.user != request.user:
        return permission_denied(request)
    return render(request, 'texts/view_text_couple.html', {'text_couple': text_couple, 'user': request.user,
                                                           'groups': get_user_group(request.user)})


@login_required
def delete_text_couple(request, text_couple_id):
    text_couple = get_object_or_404(TextCouple, pk=text_couple_id)
    if text_couple.user != request.user:
        return permission_denied(request)
    if request.method == 'POST':
        list_text_couples_copy = TextCoupleCopy.objects.filter(parent=text_couple)
        for text_couple_copy in list_text_couples_copy:
            text_couple_copy.parent = None
            text_couple_copy.message_from_moderator = 'The original has been deleted'
            text_couple_copy.save()
            text_couple_copy.canceled_request_for_moderation()
        text_couple.delete()
        return HttpResponseRedirect(reverse('texts:list_text_couples'))
    return render(request, 'texts/delete_text_couple.html', {'text_couple': text_couple, 'user': request.user,
                                                             'groups': get_user_group(request.user)})


@login_required
def change_text_couple(request, text_couple_id):
    text_couple = get_object_or_404(TextCouple, pk=text_couple_id)
    if text_couple.user != request.user:
        return permission_denied(request)
    form = TextCoupleForm(
        initial={'short': text_couple.short, 'long': text_couple.long}
    )
    if request.method == 'POST':
        form = TextCoupleForm(request.POST)
        if form.is_valid():
            short_text = form.cleaned_data['short']
            long_text = form.cleaned_data['long']
            text_couple.short = short_text
            text_couple.long = long_text
            text_couple.save()
            list_text_couples_copy = TextCoupleCopy.objects.filter(parent=text_couple)
            for text_couple_copy in list_text_couples_copy:
                text_couple_copy.canceled_request_for_moderation()
            return HttpResponseRedirect(reverse('texts:list_text_couples'))
    url_send_to_moderation = reverse('moderation:send_to_moderation', args=[text_couple_id, 'texts', 'TextCouple'])
    return render(request, 'texts/change_text_couple.html', {'form': form, 'text_couple': text_couple,
                                                             'send_to_moderation': url_send_to_moderation,
                                                             'user': request.user,
                                                             'groups': get_user_group(request.user)})
