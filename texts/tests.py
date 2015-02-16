import random

from django.core.urlresolvers import reverse
from django.test import TestCase, Client

from texts.forms import TextCoupleForm
from texts.models import TextCouple


class TextCoupleTests(TestCase):
    def test__str__return_short_part(self):
        text_couple = TextCouple(short='short part', long='long part')
        self.assertEquals('short part (long pa...)', str(text_couple))


def create_valid_random_text_couple():
    text_id = random.randint(1, 100)
    short = ''.join(random.sample('abcdefjk', 6))
    long = ''.join(random.sample('zxytrewq', 7))
    TextCouple.objects.create(id=text_id, short=short, long=long)
    return text_id, short, long


class ViewTests(TestCase):
    def test_add_text_couple_http_get(self):
        response = Client().get(reverse('texts:add_text_couple'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        self.assertContains(response, 'csrfmiddlewaretoken')
        self.assertContains(response, TextCoupleForm().as_table())

    def test_add_text_couple_http_post_empty_form(self):
        response = Client().post(reverse('texts:add_text_couple'))
        self.assertContains(response, 'This field is required')

    def test_add_text_couple_http_post_full_form(self):
        response = Client().post(reverse('texts:add_text_couple'), {'short': 'short', 'long': 'long'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(TextCouple.objects.filter(short='short', long='long').exists())
        self.assertTrue(response.url.endswith(reverse('texts:list_text_couples')))

    def test_list_text_couples_http_get_with_no_text_couples(self):
        response = Client().get(reverse('texts:list_text_couples'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No text couples were created yet')

    def test_list_text_couples_http_get_must_offer_link_for_adding(self):
        response = Client().get(reverse('texts:list_text_couples'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<a href="%s">Add text couple</a>' % reverse('texts:add_text_couple'))

    def test_list_text_couples_http_get_with_one_text_couple(self):
        TextCouple.objects.create(short='short text', long='long text')
        response = Client().get(reverse('texts:list_text_couples'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'No text couples were created yet')
        self.assertContains(response, 'short text')
        self.assertContains(response, 'long text')

    def test_list_text_couples_http_get_with_one_text_couple_random_text(self):
        text_id, short, long = create_valid_random_text_couple()
        response = Client().get(reverse('texts:list_text_couples'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, short)
        self.assertContains(response, long)

    def test_list_text_couples_http_get_with_no_text_couples_not_contains_table(self):
        response = Client().get(reverse('texts:list_text_couples'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<table width="200" border="0">', html=True)

    def test_list_text_couples_http_get_with_empty_list_text_couples(self):
        response = Client().get(reverse('texts:list_text_couples'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['text_couples']), 0)

    def test_list_text_couples_http_get_must_contain_link_to_separate_text_couples(self):
        text_id, short, long = create_valid_random_text_couple()
        response = Client().get(reverse('texts:list_text_couples'))
        self.assertContains(response, '<a href="%s">%s %s</a>' % (reverse('texts:view_text_couple',
                                                                          args=[text_id]), short, long))

    def test_text_couple_http_get(self):
        text_id, short, long = create_valid_random_text_couple()
        response = Client().get(reverse('texts:view_text_couple', args=[text_id]))
        self.assertContains(response, '%s %s' % (short, long))

    def test_del_text_couple_http_get(self):
        text_id, short, long = create_valid_random_text_couple()
        response = Client().get(reverse('texts:del_text_couple', args=[text_id]))
        self.assertContains(response, 'csrfmiddlewaretoken')
        self.assertContains(response, '<input type="submit" value="Delete">')
        self.assertContains(response, short)

    def test_del_text_couple_http_post_redirect_to_list_text_couple(self):
        text_id, short, long = create_valid_random_text_couple()
        response = Client().post(reverse('texts:del_text_couple', args=[text_id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(reverse('texts:list_text_couples')))

    def test_del_text_couple_http_get_when_no_such_text_couple(self):
        response = Client().get(reverse('texts:del_text_couple', args=[1]))
        self.assertEqual(response.status_code, 404)

    def test_change_text_couple_http_post(self):
        text_id, short, long = create_valid_random_text_couple()
        change_short = ''.join(random.sample('abcdefjk', 6))
        change_long = ''.join(random.sample('zxytrewq', 7))
        client = Client()
        client.post(reverse('texts:change_text_couple', args=[text_id]),
                    {'short': change_short, 'long': change_long})
        response = client.get(reverse('texts:list_text_couples'))
        self.assertNotContains(response, short)
        self.assertNotContains(response, long)
        self.assertContains(response, change_short)
        self.assertContains(response, change_long)

    def test_change_text_couple_http_get_when_no_such_text_couple(self):
        response = Client().get(reverse('texts:change_text_couple', args=[1]))
        self.assertEqual(response.status_code, 404)

    def test_change_text_couple_http_post_redirect_to_view_text_couple(self):
        text_id, short, long = create_valid_random_text_couple()
        change_short = 'new short'
        change_long = 'new long'
        response = Client().post(reverse('texts:change_text_couple', args=[text_id]),
                                 {'short': change_short, 'long': change_long})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(reverse('texts:list_text_couples')))

    def test_text_couple_http_get_must_contain_link_to_delete_text_couple(self):
        text_id, short, long = create_valid_random_text_couple()
        response = Client().get(reverse('texts:view_text_couple', args=[text_id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<a href="%s">Delete text couple</a>' % reverse('texts:del_text_couple',
                                                                                      args=[text_id]))

    def test_text_couple_http_get_must_contain_link_to_change_text_couple(self):
        text_id, short, long = create_valid_random_text_couple()
        response = Client().get(reverse('texts:view_text_couple', args=[text_id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<a href="%s">Change text couple</a>' % reverse('texts:change_text_couple',
                                                                                      args=[text_id]))

    def test_change_text_couple_http_get(self):
        text_id, short, long = create_valid_random_text_couple()
        response = Client().get(reverse('texts:change_text_couple', args=[text_id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        self.assertContains(response, 'csrfmiddlewaretoken')
        self.assertContains(response, TextCoupleForm().as_table())
        self.assertContains(response, 'Make edition for %s' % short)

    def test_change_text_couple_http_post_empty_form(self):
        text_id, short, long = create_valid_random_text_couple()
        response = Client().post(reverse('texts:change_text_couple', args=[text_id]))
        self.assertContains(response, 'This field is required')


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
