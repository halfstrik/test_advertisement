from django.http import HttpResponse, HttpResponseRedirect, Http404

from django.shortcuts import get_object_or_404, render
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.views.defaults import permission_denied
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist

from moderation.models import RequestForModeration


STATUSES = ((1, u'Approval pending'), (2, u'Accepted'), (3, u'Denied'),
            (4, u'Canceled'))


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
        request_for_moderation = RequestForModeration(content_object=copy, status='Approval pending')
        request_for_moderation.save()
        return HttpResponseRedirect(reverse('texts:list_text_couples'))
    return render(request, 'moderation/send_to_moderation.html', {'text_couple': advertising})
