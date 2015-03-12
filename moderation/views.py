from django.http import HttpResponse, HttpResponseRedirect

from django.shortcuts import get_object_or_404, render
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.views.defaults import permission_denied
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext
from django.template.loader import get_template
from django.db.models import Q

from moderation.models import RequestForModeration
from moderation.forms import ModerationForm


STATUSES = ((0, u'Approval pending'), (1, u'Accepted'), (2, u'Denied'), (3, u'Canceled'), (4, u'Is moderated'))


@login_required
def send_to_moderation(request, advertising_id, advertising_app, advertising_model):
    try:
        advertising_class = ContentType.objects.get(app_label=advertising_app,
                                                    model=advertising_model.lower).model_class()
    except ObjectDoesNotExist:
        return HttpResponse('No type of advertising %s' % advertising_model)
    advertising = get_object_or_404(advertising_class, pk=advertising_id)
    if advertising.user != request.user:
        return permission_denied(request)
    if request.method == 'POST':
        copy = advertising.create_copy()
        if not copy:
            return HttpResponse('Request for this text couple already exists')
        request_for_moderation = RequestForModeration(content_object=copy, status=STATUSES[0][1])
        request_for_moderation.save()
        return HttpResponseRedirect(reverse('texts:list_text_couples'))
    return render(request, 'moderation/send_to_moderation.html', {'text_couple': advertising})


@login_required
def list_request_for_moderation(request):
    try:
        group = request.user.groups.get().name
    except ObjectDoesNotExist:
        group = None
    if group == 'moderator':
        list_request_for_moderation_moderator = RequestForModeration.objects.filter(Q(status='Approval pending') | Q(
            status='Is moderated')).order_by('date_of_last_moderation')
        context = RequestContext(request,
                                 {"list_request_for_moderation_moderator": list_request_for_moderation_moderator})
        html = get_template('moderation/list_request_for_moderation.html').render(context)
        return HttpResponse(html)
    else:
        list_request_for_moderation_advertiser = list(RequestForModeration.objects.all())
        list_for_context = list()
        for request_for_moderation in list_request_for_moderation_advertiser:
            if request_for_moderation.content_object.user == request.user:
                list_for_context.append(request_for_moderation)
        context = RequestContext(request,
                                 {"list_request_for_moderation_advertiser": list_for_context})
        html = get_template('moderation/list_request_for_moderation.html').render(context)
        return HttpResponse(html)


@login_required
def moderation(request, request_for_moderation_id):
    try:
        group = request.user.groups.get().name
    except ObjectDoesNotExist:
        group = None
    if group != 'moderator':
        return HttpResponse("You are not moderator")
    request_for_moderation = get_object_or_404(RequestForModeration, id=request_for_moderation_id)
    if (request_for_moderation.status == STATUSES[1][1]) | (request_for_moderation.status == STATUSES[2][1]):
        return HttpResponse('This request has already moderated')
    if request_for_moderation.status == STATUSES[3][1]:
        return HttpResponse('This request has canceled')
    form = ModerationForm()
    request_for_moderation.status = STATUSES[4][1]
    request_for_moderation.moderator = request.user
    request_for_moderation.save()
    if request.method == 'POST':
        form = ModerationForm(request.POST)
        if form.is_valid():
            request_for_moderation.status = form.cleaned_data['status']
            request_for_moderation.message_from_moderator = form.cleaned_data['message_from_moderator']
            request_for_moderation.moderator = request.user
            request_for_moderation.save()
            return HttpResponseRedirect(reverse('moderation:list_request_for_moderation'))
    return render(request, 'moderation/moderation.html', {'form': form, 'advertiser': request_for_moderation.
                  content_object.display()})
