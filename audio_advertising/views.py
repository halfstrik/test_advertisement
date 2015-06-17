from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.template import RequestContext
from django.template.loader import get_template
from django.http import HttpResponse, HttpResponseRedirect
from django.views.defaults import permission_denied
from django.core.urlresolvers import reverse
import time
import boto

from boto.exception import S3ResponseError

from audio_advertising.forms import AudioAdvertisingForm
from audio_advertising.models import AudioAdvertising
from moderation.views import get_user_group
from test_advertisement.settings import ADVERTISER_GROUP, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_PROXY_HOST, \
    AWS_S3_PROXY_PORT, AWS_STORAGE_BUCKET_NAME

list_of_supported_types = ["Ogg data, Vorbis audio", ]


def create_new_audio_advertising(title, audio_file, user):
    audio_file._set_name('%s_%s_%s' % (user, time.time(), audio_file.name))
    audio_advertising = AudioAdvertising(title=title, audio_file=audio_file, advertiser=user)
    return audio_advertising


def is_user_in_advertiser_group(user):
    return user.groups.filter(name=ADVERTISER_GROUP).exists()


def check_file_exist(link_to_file):
    connection = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, proxy=AWS_S3_PROXY_HOST,
                                 proxy_port=AWS_S3_PROXY_PORT, is_secure=False)
    bucket = connection.get_bucket(AWS_STORAGE_BUCKET_NAME)
    try:
        file = bucket.get_key(link_to_file)
    except ConnectionError:
        file = None
    if file is None:
        existence_of_file = False
    else:
        existence_of_file = True
    return existence_of_file


def check_file_type(file):
    import magic
    file_type = magic.from_buffer(file.read())
    for supported_type in list_of_supported_types:
        if supported_type in str(file_type):
            return True
        else:
            return False


@user_passes_test(is_user_in_advertiser_group)
def add_audio_advertising(request):
    form = AudioAdvertisingForm()
    user = request.user
    if request.method == 'POST':
        form = AudioAdvertisingForm(request.POST, request.FILES)
        if form.is_valid():
            if 'audio_file' in request.FILES:
                if check_file_type(request.FILES.get('audio_file')):
                    audio_advertising = create_new_audio_advertising(form.cleaned_data['title'],
                                                                     request.FILES.get('audio_file'), request.user)
                else:
                    return HttpResponse('This type of file is not supported.')
                try:
                    audio_advertising.save()
                except (ConnectionError, S3ResponseError):
                    return HttpResponse('Storage is currently unavailable. '
                                        'Please try again later or contact your administrator.')
                return HttpResponseRedirect(reverse('audio_advertising:list_audio_advertising'))
    html = get_template('audio_advertising/add_audio_advertising.html').render(RequestContext(
        request, {'form': form, 'user': user, 'group': get_user_group(request.user)}))
    return HttpResponse(html)


@user_passes_test(is_user_in_advertiser_group)
def list_audio_advertising(request):
    try:
        list_advertising = AudioAdvertising.objects.filter(advertiser=request.user)
    except (ConnectionError, S3ResponseError):
        return HttpResponse('Storage is currently unavailable. Please try again later or contact your administrator.')
    html = get_template('audio_advertising/list_audio_advertising.html').render(
        RequestContext(request, {'list_advertising': list_advertising,
                                 'user': request.user, 'groups': get_user_group(request.user)}))
    return HttpResponse(html)


@user_passes_test(is_user_in_advertiser_group)
def view_audio_advertising(request, audio_advertising_id):
    audio_advertising = get_object_or_404(AudioAdvertising, pk=audio_advertising_id)
    if audio_advertising.advertiser != request.user:
        return permission_denied(request)
    existence_of_file = check_file_exist(audio_advertising.audio_file)
    if existence_of_file is False:
        return HttpResponse('Storage is currently unavailable. '
                            'Please try again later or contact your administrator.')
    return render(request, 'audio_advertising/view_audio_advertising.html', {'audio_advertising': audio_advertising,
                                                                             'user': request.user,
                                                                             'groups': get_user_group(request.user)})


@user_passes_test(is_user_in_advertiser_group)
def delete_audio_advertising(request, audio_advertising_id):
    audio_advertising = get_object_or_404(AudioAdvertising, pk=audio_advertising_id)
    if audio_advertising.advertiser != request.user:
        return permission_denied(request)
    if request.method == 'POST':
        try:
            audio_advertising.audio_file.delete()
            audio_advertising.delete()
        except (ConnectionError, S3ResponseError):
            return HttpResponse('DB or storage is currently unavailable. '
                                'Please try again later or contact your administrator.')
        return HttpResponseRedirect(reverse('audio_advertising:list_audio_advertising'))
    return render(request, 'audio_advertising/delete_audio_advertising.html',
                  {'audio_advertising': audio_advertising, 'user': request.user,
                   'groups': get_user_group(request.user)})


@user_passes_test(is_user_in_advertiser_group)
def change_audio_advertising(request, audio_advertising_id):
    audio_advertising = get_object_or_404(AudioAdvertising, pk=audio_advertising_id)
    if audio_advertising.advertiser != request.user:
        return permission_denied(request)
    form = AudioAdvertisingForm(initial={'title': audio_advertising.title})
    if request.method == 'POST':
        form = AudioAdvertisingForm(request.POST, request.FILES)
        if form.is_valid():
            if 'audio_file' in request.FILES:
                title = form.cleaned_data['title']
                audio_file = request.FILES.get('audio_file')
                if not(check_file_type(audio_file)):
                    return HttpResponse('This type of file is not supported.')
                audio_file._set_name('%s_%s_%s' % (request.user, time.time(), audio_file.name))
                audio_advertising.title = title
                try:
                    audio_advertising.audio_file.delete()
                except (ConnectionError, S3ResponseError):
                    return HttpResponse('No deleted file')
                audio_advertising.audio_file = audio_file
                try:
                    audio_advertising.save()
                except (ConnectionError, S3ResponseError):
                    return HttpResponse('Storage or DB is currently unavailable. '
                                        'Please try again later or contact your administrator.')
                return HttpResponseRedirect(reverse('audio_advertising:list_audio_advertising'))
    html = get_template('audio_advertising/change_audio_advertising.html').render(RequestContext(
        request, {'form': form, 'audio_advertising': audio_advertising, 'user': request.user,
                  'group': get_user_group(request.user)}))
    return HttpResponse(html)
