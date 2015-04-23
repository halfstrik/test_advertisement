import random
import os
import unittest

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from test_advertisement.settings import ADVERTISER_GROUP, BASE_DIR, LOGIN_URL
from audio_advertising.models import AudioAdvertising
from audio_advertising.forms import AudioAdvertisingForm
from texts.tests import get_client_and_user_of_create_random_user_and_login
from moderation.tests import create_group


def create_audio_file():
    file_name = ''.join(random.sample('abcdefjk', 7))
    audio_file = open('%s.ogg' % file_name, 'w')
    audio_file.close()
    return file_name, audio_file


def create_audio_advertising():
    title = ''.join(random.sample('abcdefjk', 7))
    file_name, audio_file = create_audio_file()
    return title, file_name, audio_file


class AudioAdvertisingTests(TestCase):
    def test__str__return_short_part(self):
        title, file_name, audio_file = create_audio_advertising()
        audio_advertising = AudioAdvertising(title=title, audio_file=audio_file)
        self.assertEquals('%s %s.ogg' % (title, file_name), str(audio_advertising))
        os.remove("%s/%s.ogg" % (BASE_DIR, file_name))


def add_user_to_group(user, group_name):
    group = create_group(group_name)
    user.groups.add(group)


def add_new_audio_advertising(client):
    title = ''.join(random.sample('abcdefjk', 7))
    with open('test.ogg', 'rb') as audio_file:
        client.post(reverse('audio_advertising:add_audio_advertising'), {'title': title, 'audio_file': audio_file})
    audio_file.close()
    return title, audio_file


class ViewTests(TestCase):
    def test_add_audio_advertising_http_get(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        add_user_to_group(user, ADVERTISER_GROUP)
        response = client.get(reverse('audio_advertising:add_audio_advertising'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        self.assertContains(response, 'csrfmiddlewaretoken')
        self.assertContains(response, AudioAdvertisingForm().as_table())

    def test_add_audio_advertising_http_post_empty_form(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        add_user_to_group(user, ADVERTISER_GROUP)
        response = client.post(reverse('audio_advertising:add_audio_advertising'))
        self.assertContains(response, 'This field is required')

    def test_add_audio_advertising_http_post_empty_audio_file(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        add_user_to_group(user, ADVERTISER_GROUP)
        title = ''.join(random.sample('abcdefjk', 7))
        response = client.post(reverse('audio_advertising:add_audio_advertising'), {'title': title, })
        self.assertContains(response, 'This field is required')

    @unittest.skip
    def test_add_audio_advertising_http_post_full_form(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        add_user_to_group(user, ADVERTISER_GROUP)
        title = ''.join(random.sample('abcdefjk', 7))
        with open('test.ogg', 'rb') as audio_file:
            response = client.post(reverse('audio_advertising:add_audio_advertising'),
                                   {'title': title, 'audio_file': audio_file})
        audio_file.close()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(AudioAdvertising.objects.filter(title=title, advertiser=user.id).exists())
        self.assertTrue(response.url.endswith(reverse('audio_advertising:list_audio_advertising')))

    def test_add_audio_advertising_http_get_anonymous_user(self):
        response = Client().get(reverse('audio_advertising:add_audio_advertising'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(LOGIN_URL + '?next=' +
                                              reverse('audio_advertising:add_audio_advertising')))

    def test_add_audio_advertising_http_post_anonymous_user(self):
        title = ''.join(random.sample('abcdefjk', 7))
        with open('test.ogg', 'rb') as audio_file:
            response = Client().post(reverse('audio_advertising:add_audio_advertising'),
                                     {'title': title, 'audio_file': audio_file})
        audio_file.close()
        self.assertFalse(AudioAdvertising.objects.filter(title=title, audio_file=audio_file).exists())
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(LOGIN_URL + '?next=' +
                                              reverse('audio_advertising:add_audio_advertising')))

    def test_list_audio_advertising_http_get_anonymous_user(self):
        response = Client().get(reverse('audio_advertising:list_audio_advertising'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(LOGIN_URL + '?next=' +
                                              reverse('audio_advertising:list_audio_advertising')))

    def test_list_audio_advertising_http_get_with_no_audio_advertising(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        add_user_to_group(user, ADVERTISER_GROUP)
        response = client.get(reverse('audio_advertising:list_audio_advertising'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No audio advertising were created yet.')

    def test_list_audio_advertising_http_get_must_offer_link_for_adding(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        add_user_to_group(user, ADVERTISER_GROUP)
        response = client.get(reverse('audio_advertising:list_audio_advertising'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<a href="%s">Add audio advertising</a>'
                            % reverse('audio_advertising:add_audio_advertising'))
        self.assertNotContains(response, '<table width="800" border="0">', html=True)

    @unittest.skip
    def test_list_audio_advertising_http_get_with_one_audio_advertising(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        add_user_to_group(user, ADVERTISER_GROUP)
        title, audio_file = add_new_audio_advertising(client)
        response = client.get(reverse('audio_advertising:list_audio_advertising'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'No text couples were created yet')
        self.assertContains(response, title)
        self.assertContains(response, audio_file.name)

    def test_list_audio_advertising_http_get_with_empty_list_text_couples(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        add_user_to_group(user, ADVERTISER_GROUP)
        response = client.get(reverse('audio_advertising:list_audio_advertising'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['list_advertising']), 0)

    @unittest.skip
    def test_list_audio_advertising_http_get_must_contain_link_to_separate_audio_advertising(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        add_user_to_group(user, ADVERTISER_GROUP)
        title, audio_file = add_new_audio_advertising(client)
        audio_advertising = get_object_or_404(AudioAdvertising, title=title)
        response = client.get(reverse('audio_advertising:list_audio_advertising'))
        self.assertContains(response, '<a href="%s">Editing</a>' % (reverse('audio_advertising:view_audio_advertising',
                                                                            args=[audio_advertising.id])))

    @unittest.skip
    def test_list_audio_advertising_http_get_text_couple_other_user(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        add_user_to_group(user, ADVERTISER_GROUP)
        title, audio_file = add_new_audio_advertising(client)
        client, user = get_client_and_user_of_create_random_user_and_login()
        add_user_to_group(user, ADVERTISER_GROUP)
        response = client.get(reverse('audio_advertising:list_audio_advertising'))
        audio_advertising = get_object_or_404(AudioAdvertising, title=title)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, audio_advertising.title)
        self.assertNotContains(response, audio_advertising.audio_file.name)

    def test_audio_advertising_http_get_anonymous_user_audio_advertising_does_not_exist(self):
        audio_advertising_id = random.randint(1, 100)
        response = Client().get(reverse('audio_advertising:view_audio_advertising', args=[audio_advertising_id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(LOGIN_URL + '?next=' + reverse('audio_advertising:view_audio_advertising',
                                                                             args=[audio_advertising_id])))

    def test_audio_advertising_http_get_audio_advertising_does_not_exist(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        add_user_to_group(user, ADVERTISER_GROUP)
        audio_advertising_id = random.randint(1, 100)
        response = client.get(reverse('audio_advertising:view_audio_advertising', args=[audio_advertising_id]))
        self.assertEqual(response.status_code, 404)

    def test_del_audio_advertising_couple_http_get_anonymous_user(self):
        audio_advertising_id = random.randint(1, 100)
        response = Client().get(reverse('audio_advertising:delete_audio_advertising', args=[audio_advertising_id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(LOGIN_URL + '?next=' +
                                              reverse('audio_advertising:delete_audio_advertising',
                                                      args=[audio_advertising_id])))

    def test_del_audio_advertising_http_post_anonymous_user(self):
        audio_advertising_id = random.randint(1, 100)
        response = Client().post(reverse('audio_advertising:delete_audio_advertising', args=[audio_advertising_id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(LOGIN_URL + '?next=' +
                                              reverse('audio_advertising:delete_audio_advertising',
                                                      args=[audio_advertising_id])))

    def test_change_audio_advertising_http_get_anonymous_user(self):
        audio_advertising_id = random.randint(1, 100)
        response = Client().get(reverse('audio_advertising:change_audio_advertising', args=[audio_advertising_id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(LOGIN_URL + '?next=' +
                                              reverse('audio_advertising:change_audio_advertising',
                                                      args=[audio_advertising_id])))

    def test_change_audio_advertising_http_post_anonymous_user(self):
        audio_advertising_id = random.randint(1, 100)
        title = ''.join(random.sample('abcdefjk', 7))
        with open('test.ogg', 'rb') as audio_file:
            response = Client().post(reverse('audio_advertising:change_audio_advertising', args=[audio_advertising_id]),
                                     {'title': title, 'audio_file': audio_file})
        audio_file.close()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(LOGIN_URL + '?next=' +
                                              reverse('audio_advertising:change_audio_advertising',
                                                      args=[audio_advertising_id])))

    def test_change_audio_advertising_http_get_when_no_such_text_couple(self):
        text_id = random.randint(1, 100)
        client, user = get_client_and_user_of_create_random_user_and_login()
        add_user_to_group(user, ADVERTISER_GROUP)
        response = client.get(reverse('audio_advertising:change_audio_advertising', args=[text_id]))
        self.assertEqual(response.status_code, 404)