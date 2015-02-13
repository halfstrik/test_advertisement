from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from texts.forms import TextCoupleForm
from texts.models import TextCouple


class TextCoupleTests(TestCase):
    def test__str__return_short_part(self):
        text_couple = TextCouple(short='short part', long='long part')
        self.assertEquals('short part (long pa...)', str(text_couple))


class ViewTests(TestCase):
    def test_add_text_couple_http_get(self):
        client = Client()
        response = client.get(reverse('texts:add_text_couple'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        self.assertContains(response, 'csrfmiddlewaretoken')
        self.assertContains(response, TextCoupleForm().as_table())

    def test_add_text_couple_http_post_empty_form(self):
        client = Client()
        response = client.post(reverse('texts:add_text_couple'))
        self.assertContains(response, 'This field is required')

    def test_add_text_couple_http_post_full_form(self):
        client = Client()
        response = client.post(reverse('texts:add_text_couple'), {'short': 'short', 'long': 'long'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(TextCouple.objects.filter(short='short', long='long').exists())


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

    def test_list_text_couples_http_get_with_no_text_couples(self):
        client = Client()
        response = client.get(reverse('texts:list_text_couples'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No text couples were created yet')

    def test_list_text_couples_http_get_must_offer_link_for_adding(self):
        client = Client()
        response = client.get(reverse('texts:list_text_couples'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<a href="%s">Add text couple</a>' % reverse('texts:add_text_couple'))

    def test_list_text_couples_http_get_with_one_text_couple(self):
        TextCouple.objects.create(short='short text', long='long text')
        client = Client()
        response = client.get(reverse('texts:list_text_couples'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'No text couples were created yet')
        self.assertContains(response, 'short text')
        self.assertContains(response, 'long text')
