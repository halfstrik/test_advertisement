from django.http import HttpResponse, HttpResponseRedirect

from django.shortcuts import get_object_or_404, render
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.defaults import permission_denied
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext
from django.template.loader import get_template
from django.db.models import Q
from test_advertisement.settings import MODERATORS_GROUP

from moderation.models import RequestForModeration
from moderation.forms import ModerationForm


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
        request_for_moderation = RequestForModeration(content_object=copy, status=RequestForModeration.APPROVAL_PENDING)
        request_for_moderation.save()
        return HttpResponseRedirect(reverse('texts:list_text_couples'))
    return render(request, 'moderation/send_to_moderation.html', {'text_couple': advertising})


def list_request_for_moderation_to_moderator(request):
    list_for_context = RequestForModeration.objects.filter(Q(status=RequestForModeration.APPROVAL_PENDING) | Q(
        status=RequestForModeration.IS_MODERATED)).order_by('date_of_last_moderation')
    context = RequestContext(request, {"list_request_for_moderation_moderator": list_for_context})
    html = get_template('moderation/list_request_for_moderation_to_moderator.html').render(context)
    return html


def list_request_for_moderation_to_advertiser(request):
    list_request_for_moderation_advertiser = list(RequestForModeration.objects.all())
    list_for_context = list()
    for request_for_moderation in list_request_for_moderation_advertiser:
        if request_for_moderation.content_object.user == request.user:
            list_for_context.append(request_for_moderation)
    context = RequestContext(request, {"list_request_for_moderation_advertiser": list_for_context})
    html = get_template('moderation/list_request_for_moderation_to_advertiser.html').render(context)
    return html


@login_required
def list_request_for_moderation(request):
    try:
        group = request.user.groups.get().name
    except ObjectDoesNotExist:
        group = None
    if group == 'Moderator':
        return HttpResponse(list_request_for_moderation_to_moderator(request))
    else:
        return HttpResponse(list_request_for_moderation_to_advertiser(request))


class ModerationError(Exception):
        pass


def moderation(user, request_for_moderation, status, message):
    if status == RequestForModeration.DENIED:
        status_request = RequestForModeration.DENIED
    elif status == RequestForModeration.ACCEPTED:
        status_request = RequestForModeration.ACCEPTED
    else:
        raise ModerationError
    request_for_moderation.status = status_request
    request_for_moderation.message_from_moderator = message
    request_for_moderation.moderator = user
    request_for_moderation.save()


def begin_moderation(user, request_for_moderation):
    if request_for_moderation.status in (RequestForModeration.ACCEPTED, RequestForModeration.DENIED,
                                         RequestForModeration.CANCELED):
        raise ModerationError
    elif request_for_moderation.status == RequestForModeration.IS_MODERATED:
        if request_for_moderation.moderator != user:
            raise ModerationError
    else:
        request_for_moderation.status = RequestForModeration.IS_MODERATED
        request_for_moderation.moderator = user
        request_for_moderation.save()


def is_user_in_moderator_group(user):
    return user.groups.filter(name=MODERATORS_GROUP).exists()


@user_passes_test(is_user_in_moderator_group)
def initiate_moderation(request, request_for_moderation_id):
    request_for_moderation = get_object_or_404(RequestForModeration, id=request_for_moderation_id)
    try:
        begin_moderation(request.user, request_for_moderation)
    except ModerationError:
        return HttpResponse("Can't initiate moderation as request is not in APPROVAL_PENDING state")
    form = ModerationForm()
    if request.method == 'POST':
        form = ModerationForm(request.POST)
        if form.is_valid():
            try:
                moderation(request.user, request_for_moderation, form.cleaned_data['status'],
                           form.cleaned_data['message_from_moderator'])
            except ModerationError:
                return HttpResponse("You can select the status of ACCEPTED or DENIED")
            return HttpResponseRedirect(reverse('moderation:list_request_for_moderation'))
    return render(request, 'moderation/moderation.html', {'form': form, 'advertiser': request_for_moderation.
                  content_object.display()})
