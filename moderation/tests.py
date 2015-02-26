import random

from django.core.urlresolvers import reverse
from django.test import TestCase, Client

from texts.models import TextCouple
from test_advertisement.settings import LOGIN_URL
from moderation.models import RequestForModeration, TextCoupleCopy
from texts.tests import create_valid_random_text_couple, get_client_and_user_of_create_random_user_and_login


class ModerationViewTests(TestCase):
    def test_view_send_to_moderation_http_get_anonymous_user(self):
        text_id = random.randint(1, 100)
        response = Client().get(reverse('moderation:send_to_moderation', args=[text_id, 'texts', 'TextCouple']))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(LOGIN_URL + '?next=' +
                                              reverse('moderation:send_to_moderation', args=[text_id, 'texts',
                                                                                             'TextCouple'])))

    def test_view_send_to_moderation_http_post_anonymous_user(self):
        text_id = random.randint(1, 100)
        response = Client().post(reverse('moderation:send_to_moderation', args=[text_id, 'texts', 'TextCouple']))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(LOGIN_URL + '?next=' +
                                              reverse('moderation:send_to_moderation', args=[text_id, 'texts',
                                                                                             'TextCouple'])))

    def test_view_send_to_moderation_http_get(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        text_id, short, long = create_valid_random_text_couple(user)
        response = client.get(reverse('moderation:send_to_moderation', args=[text_id, 'texts', 'TextCouple']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        self.assertContains(response, 'csrfmiddlewaretoken')
        self.assertContains(response, '<input type="submit" value="OK">')
        self.assertContains(response, 'Send a request to moderation for advertising %s'
                            % TextCouple.objects.get(id=text_id))

    def test_view_send_to_moderation_http_post(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        text_id, short, long = create_valid_random_text_couple(user)
        response = client.post(reverse('moderation:send_to_moderation', args=[text_id, 'texts', 'TextCouple']))
        self.assertTrue(response.url.endswith(reverse('texts:list_text_couples')))
        self.assertTrue(RequestForModeration.objects.filter(object_id=TextCoupleCopy.objects.filter(
            parent_text_couple=TextCouple.objects.filter(id=text_id))))
        self.assertNotContains(response, 'Request for this text couple already exists', status_code=302)
        self.assertTrue(response.url.endswith(reverse('texts:list_text_couples')))

    def test_view_send_to_moderation_http_post_send_request_other_user(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        text_id, short, long = create_valid_random_text_couple(user)
        new_client, new_user = get_client_and_user_of_create_random_user_and_login()
        new_response = new_client.post(reverse('moderation:send_to_moderation', args=[text_id, 'texts', 'TextCouple']))
        self.assertEqual(new_response.status_code, 403)
        self.assertFalse(RequestForModeration.objects.filter(object_id=TextCoupleCopy.objects.filter(
            parent_text_couple=TextCouple.objects.filter(id=text_id))))

    def test_view_send_to_moderation_http_post_send_exists_request(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        text_id, short, long = create_valid_random_text_couple(user)
        client.post(reverse('moderation:send_to_moderation', args=[text_id, 'texts', 'TextCouple']))
        response = client.post(reverse('moderation:send_to_moderation', args=[text_id, 'texts', 'TextCouple']))
        self.assertContains(response, 'Request for this text couple already exists')

    def test_view_send_to_moderation_http_post_send_request_with_nonexistent_advertising_class(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        text_id, short, long = create_valid_random_text_couple(user)
        advertising_class = ''.join(random.sample('abcdefjk', 6))
        response = client.post(reverse('moderation:send_to_moderation', args=[text_id, 'texts', advertising_class]))
        self.assertContains(response, 'No type of advertising %s' % advertising_class)
