import random

from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from django.contrib.auth.models import User

from texts.forms import TextCoupleForm
from texts.models import TextCouple
from test_advertisement.settings import LOGIN_URL
from moderation.models import RequestForModeration


class TextCoupleTests(TestCase):
    def test__str__return_short_part(self):
        short, long = create_two_random_text()
        text_couple = TextCouple(short=short, long=long)
        self.assertEquals('%s (%s...)' % (short, long[:7]), str(text_couple))


def create_two_random_text():
    first_text = ''.join(random.sample('abcdefjk', 6))
    second_text = ''.join(random.sample('zxytrewq', 7))
    return first_text, second_text


def create_valid_random_text_couple(user):
    text_id = random.randint(1, 100)
    short, long = create_two_random_text()
    TextCouple.objects.create(id=text_id, short=short, long=long, user=user)
    return text_id, short, long


def get_client_and_user_of_create_random_user_and_login():
    username, password = create_two_random_text()
    user = User.objects.create_user(username=username, password=password)
    client = Client()
    client.login(username=username, password=password)
    return client, user


class ViewTests(TestCase):
    def test_add_text_couple_http_get(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        response = client.get(reverse('texts:add_text_couple'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        self.assertContains(response, 'csrfmiddlewaretoken')
        self.assertContains(response, TextCoupleForm().as_table())

    def test_add_text_couple_http_post_empty_form(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        response = client.post(reverse('texts:add_text_couple'))
        self.assertContains(response, 'This field is required')

    def test_add_text_couple_http_post_full_form(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        response = client.post(reverse('texts:add_text_couple'), {'short': 'short',
                                                                  'long': 'long'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(TextCouple.objects.filter(short='short',
                                                  long='long',
                                                  user_id=user.id).exists())
        self.assertTrue(response.url.endswith(reverse('texts:list_text_couples')))

    def test_add_text_couple_http_get_anonymous_user(self):
        response = Client().get(reverse('texts:add_text_couple'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(LOGIN_URL + '?next=' + reverse('texts:add_text_couple')))

    def test_add_text_couple_http_post_anonymous_user(self):
        short, long = create_two_random_text()
        response = Client().post(reverse('texts:add_text_couple'), {'short': short,
                                                                    'long': long})
        self.assertFalse(TextCouple.objects.filter(short=short,
                                                   long=long).exists())
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(LOGIN_URL + '?next=' + reverse('texts:add_text_couple')))

    def test_list_text_couple_http_get_anonymous_user(self):
        response = Client().get(reverse('texts:add_text_couple'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(LOGIN_URL + '?next=' + reverse('texts:add_text_couple')))

    def test_list_text_couples_http_get_with_no_text_couples(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        response = client.get(reverse('texts:list_text_couples'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No text couples were created yet')

    def test_list_text_couples_http_get_must_offer_link_for_adding(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        response = client.get(reverse('texts:list_text_couples'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<a href="%s">Add text couple</a>' % reverse('texts:add_text_couple'))

    def test_list_text_couples_http_get_with_one_text_couple(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        TextCouple.objects.create(short='short text', long='long text', user=user)
        response = client.get(reverse('texts:list_text_couples'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'No text couples were created yet')
        self.assertContains(response, 'short text')
        self.assertContains(response, 'long text')

    def test_list_text_couples_http_get_with_one_text_couple_random_text(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        text_id, short, long = create_valid_random_text_couple(user)
        response = client.get(reverse('texts:list_text_couples'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, short)
        self.assertContains(response, long)

    def test_list_text_couples_http_get_with_no_text_couples_not_contains_table(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        response = client.get(reverse('texts:list_text_couples'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<table width="800" border="0">', html=True)

    def test_list_text_couples_http_get_with_empty_list_text_couples(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        response = client.get(reverse('texts:list_text_couples'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['text_couples']), 0)

    def test_list_text_couples_http_get_must_contain_link_to_separate_text_couples(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        text_id, short, long = create_valid_random_text_couple(user)
        response = client.get(reverse('texts:list_text_couples'))
        self.assertContains(response, '<a href="%s">%s %s</a>' % (reverse('texts:view_text_couple',
                                                                          args=[text_id]), short, long))

    def test_list_text_couples_http_get_text_couple_other_user(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        text_id, short, long = create_valid_random_text_couple(user)
        client, user = get_client_and_user_of_create_random_user_and_login()
        response = client.get(reverse('texts:list_text_couples'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, short)
        self.assertNotContains(response, long)

    def test_list_text_couples_http_get_text_couples_different_user(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        text_id, short, long = create_valid_random_text_couple(user)
        client, new_user = get_client_and_user_of_create_random_user_and_login()
        new_text_id, new_short, new_long = create_valid_random_text_couple(new_user)
        response = client.get(reverse('texts:list_text_couples'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, short)
        self.assertNotContains(response, long)
        self.assertContains(response, new_short)
        self.assertContains(response, new_long)

    def test_text_couple_http_get_anonymous_user_text_couples_does_not_exist(self):
        text_id = random.randint(1, 100)
        response = Client().get(reverse('texts:view_text_couple', args=[text_id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(LOGIN_URL + '?next=' + reverse('texts:view_text_couple', args=[text_id])))

    def test_text_couple_http_get_anonymous_user(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        text_id, short, long = create_valid_random_text_couple(user)
        response = Client().get(reverse('texts:view_text_couple', args=[text_id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(LOGIN_URL + '?next=' + reverse('texts:view_text_couple', args=[text_id])))

    def test_text_couple_http_get(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        text_id, short, long = create_valid_random_text_couple(user)
        response = client.get(reverse('texts:view_text_couple', args=[text_id]))
        self.assertContains(response, '%s %s' % (short, long))

    def test_text_couple_http_get_must_contain_link_to_change_text_couple(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        text_id, short, long = create_valid_random_text_couple(user)
        response = client.get(reverse('texts:view_text_couple', args=[text_id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<a href="%s">Change text couple</a>' % reverse('texts:change_text_couple',
                                                                                      args=[text_id]))

    def test_text_couple_http_get_must_contain_link_to_delete_text_couple(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        text_id, short, long = create_valid_random_text_couple(user)
        response = client.get(reverse('texts:view_text_couple', args=[text_id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<a href="%s">Delete text couple</a>' % reverse('texts:del_text_couple',
                                                                                      args=[text_id]))

    def test_text_couple_http_get_text_couple_other_user(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        text_id, short, long = create_valid_random_text_couple(user)
        new_client, new_user = get_client_and_user_of_create_random_user_and_login()
        response = new_client.get(reverse('texts:view_text_couple', args=[text_id]))
        self.assertEqual(response.status_code, 403)

    def test_text_couple_http_get_text_couple_does_not_exist(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        text_id = random.randint(1, 100)
        response = client.get(reverse('texts:view_text_couple', args=[text_id]))
        self.assertEqual(response.status_code, 404)

    def test_del_text_couple_http_get_anonymous_user(self):
        text_id = random.randint(1, 100)
        response = Client().get(reverse('texts:del_text_couple', args=[text_id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(LOGIN_URL + '?next=' + reverse('texts:del_text_couple', args=[text_id])))

    def test_del_text_couple_http_post_anonymous_user(self):
        text_id = random.randint(1, 100)
        response = Client().post(reverse('texts:del_text_couple', args=[text_id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(LOGIN_URL + '?next=' + reverse('texts:del_text_couple', args=[text_id])))

    def test_del_text_couple_http_post_anonymous_user_not_delete(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        text_id, short, long = create_valid_random_text_couple(user)
        Client().post(reverse('texts:del_text_couple', args=[text_id]))
        self.assertTrue(TextCouple.objects.filter(id=text_id).exists())

    def test_del_text_couple_http_get(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        text_id, short, long = create_valid_random_text_couple(user)
        response = client.get(reverse('texts:del_text_couple', args=[text_id]))
        self.assertContains(response, 'csrfmiddlewaretoken')
        self.assertContains(response, '<input type="submit" value="Delete">')
        self.assertContains(response, short)

    def test_del_text_couple_http_post(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        text_id, short, long = create_valid_random_text_couple(user)
        client.post(reverse('texts:del_text_couple', args=[text_id]))
        self.assertFalse(TextCouple.objects.filter(short=short,
                                                   long=long,
                                                   user_id=user.id).exists())

    def test_del_text_couple_http_post_redirect_to_list_text_couple(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        text_id, short, long = create_valid_random_text_couple(user)
        response = client.post(reverse('texts:del_text_couple', args=[text_id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(reverse('texts:list_text_couples')))

    def test_del_text_couple_http_get_when_no_such_text_couple(self):
        text_id = random.randint(1, 100)
        client, user = get_client_and_user_of_create_random_user_and_login()
        response = client.get(reverse('texts:del_text_couple', args=[text_id]))
        self.assertEqual(response.status_code, 404)

    def test_del_text_couple_http_post_delete_text_couple_other_user(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        text_id, short, long = create_valid_random_text_couple(user)
        new_client, new_user = get_client_and_user_of_create_random_user_and_login()
        new_response = new_client.post(reverse('texts:del_text_couple', args=[text_id]))
        response = client.get(reverse('texts:list_text_couples'))
        self.assertContains(response, short)
        self.assertContains(response, long)
        self.assertEqual(new_response.status_code, 403)

    def test_change_text_couple_http_get_anonymous_user(self):
        text_id = random.randint(1, 100)
        response = Client().get(reverse('texts:change_text_couple', args=[text_id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(LOGIN_URL + '?next=' +
                                              reverse('texts:change_text_couple', args=[text_id])))

    def test_change_text_couple_http_post_anonymous_user(self):
        text_id = random.randint(1, 100)
        response = Client().post(reverse('texts:change_text_couple', args=[text_id]),
                                 {'short': 'short',
                                  'long': 'long'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(LOGIN_URL + '?next=' +
                                              reverse('texts:change_text_couple', args=[text_id])))

    def test_change_text_couple_http_post(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        text_id, short, long = create_valid_random_text_couple(user)
        change_long, change_short = create_two_random_text()
        client.post(reverse('texts:change_text_couple', args=[text_id]),
                    {'short': change_short,
                     'long': change_long})
        self.assertFalse(TextCouple.objects.filter(short=short,
                                                   long=long,
                                                   user_id=user.id).exists())
        self.assertTrue(TextCouple.objects.filter(short=change_short,
                                                  long=change_long,
                                                  user_id=user.id).exists())

    def test_change_text_couple_http_get_when_no_such_text_couple(self):
        text_id = random.randint(1, 100)
        client, user = get_client_and_user_of_create_random_user_and_login()
        response = client.get(reverse('texts:change_text_couple', args=[text_id]))
        self.assertEqual(response.status_code, 404)

    def test_change_text_couple_http_post_redirect_to_view_text_couple(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        text_id, short, long = create_valid_random_text_couple(user)
        change_short, change_long = create_two_random_text()
        response = client.post(reverse('texts:change_text_couple', args=[text_id]),
                               {'short': change_short,
                                'long': change_long})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(reverse('texts:list_text_couples')))

    def test_change_text_couple_http_post_anonymous_user_change_text_couple_other_user(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        text_id, short, long = create_valid_random_text_couple(user)
        change_short, change_long = create_two_random_text()
        Client().post(reverse('texts:change_text_couple', args=[text_id]),
                      {'short': change_short,
                      'long': change_long})
        self.assertTrue(TextCouple.objects.filter(short=short,
                                                  long=long).exists())

    def test_change_text_couple_http_get(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        text_id, short, long = create_valid_random_text_couple(user)
        response = client.get(reverse('texts:change_text_couple', args=[text_id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        self.assertContains(response, 'csrfmiddlewaretoken')
        self.assertContains(response, TextCoupleForm().as_table())
        self.assertContains(response, 'Make edition for %s' % short)

    def test_change_text_couple_http_post_empty_form(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        text_id, short, long = create_valid_random_text_couple(user)
        response = client.post(reverse('texts:change_text_couple', args=[text_id]))
        self.assertContains(response, 'This field is required')

    def test_change_text_couple_http_post_change_text_couple_other_user(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        text_id, short, long = create_valid_random_text_couple(user)
        change_short, change_long = create_two_random_text()
        new_client, new_user = get_client_and_user_of_create_random_user_and_login()
        new_response = new_client.post(reverse('texts:change_text_couple', args=[text_id]),
                                       {'short': change_short,
                                        'long': change_long})
        self.assertEqual(new_response.status_code, 403)
        self.assertTrue(TextCouple.objects.filter(short=short,
                                                  long=long,
                                                  user_id=user.id).exists())
        self.assertFalse(TextCouple.objects.filter(short=change_short,
                                                   long=change_long,
                                                   user_id=user.id).exists())

    def test_view_text_couple_http_get_must_offer_link_request_for_moderation(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        text_id, short, long = create_valid_random_text_couple(user)
        response = client.get(reverse('texts:view_text_couple', args=[text_id]))
        self.assertContains(response, '<a href="%s">Send to moderation</a>' % reverse('moderation:send_to_moderation',
                                                                                      args=[text_id, 'texts',
                                                                                            'TextCouple']))


class FormTests(TestCase):
    def test_TextCoupleForm_with_short_text_len_equals_31(self):
        self.assertFalse(TextCoupleForm({'short': '0123456789' * 3 + 'a',
                                         'long': 'test'}).is_valid())

    def test_TextCoupleForm_with_short_text_len_equals_30(self):
        self.assertTrue(TextCoupleForm({'short': '0123456789' * 3,
                                        'long': 'test'}).is_valid())

    def test_TextCoupleForm_with_short_text_len_equals_2(self):
        self.assertFalse(TextCoupleForm({'short': '01',
                                         'long': 'test'}).is_valid())

    def test_TextCoupleForm_with_short_text_len_equals_3(self):
        self.assertTrue(TextCoupleForm({'short': '012',
                                        'long': 'test'}).is_valid())

    def test_TextCoupleForm_with_short_text_label(self):
        self.assertEquals(TextCoupleForm({'short': '012',
                                          'long': 'test'}).fields['short'].label,
                          'Enter title, make it short')

    def test_TextCoupleForm_with_long_text_label(self):
        self.assertEquals(TextCoupleForm({'short': '012',
                                          'long': 'test'}).fields['long'].label,
                          'Enter description')

    def test_TextCoupleForm_with_long_text_len_equals_141(self):
        self.assertFalse(TextCoupleForm({'short': '0124',
                                         'long': '0123456789' * 14 + 'a'}).is_valid())

    def test_TextCoupleForm_with_long_text_len_equals_140(self):
        self.assertTrue(TextCoupleForm({'short': '0124',
                                        'long': '0123456789' * 14}).is_valid())
