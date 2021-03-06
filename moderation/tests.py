import random

from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from django.contrib.auth.models import Group

from texts.models import TextCouple, TextCoupleCopy
from test_advertisement.settings import LOGIN_URL, MODERATORS_GROUP
from moderation.models import RequestForModeration
from texts.tests import create_valid_random_text_couple, get_client_and_user_of_create_random_user_and_login, \
    create_two_random_text
from moderation.forms import ModerationForm
from moderation.views import begin_moderation, ModerationError, moderation, get_user_group
from django.contrib.auth.models import User


def create_group(group_name):
    try:
        group = Group.objects.get(name=group_name)
    except:
        group = Group.objects.create(name=group_name)
    return group


def create_users_request_to_moderation_and_text_couple_copy():
    client, user = get_client_and_user_of_create_random_user_and_login()
    text_couple = create_valid_random_text_couple(user)
    client.post(reverse('moderation:send_to_moderation', args=[text_couple.id, 'texts', 'TextCouple']))
    text_couple_copy = TextCoupleCopy.objects.get(short=text_couple.short, long=text_couple.long, parent=text_couple)
    request_for_moderation = RequestForModeration.objects.get(object_id=text_couple_copy.id)
    group = create_group(MODERATORS_GROUP)
    client_moderator, user_moderator = get_client_and_user_of_create_random_user_and_login()
    user_moderator.groups.add(group)
    return client, client_moderator, request_for_moderation, text_couple_copy


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
        text_couple = create_valid_random_text_couple(user)
        response = client.get(reverse('moderation:send_to_moderation', args=[text_couple.id, 'texts', 'TextCouple']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        self.assertContains(response, 'csrfmiddlewaretoken')
        self.assertContains(response, '<input type="submit" value="OK">')
        self.assertContains(response, 'Send a request to moderation for advertising %s'
                            % TextCouple.objects.get(id=text_couple.id))

    def test_view_send_to_moderation_http_post(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        text_couple = create_valid_random_text_couple(user)
        response = client.post(reverse('moderation:send_to_moderation', args=[text_couple.id, 'texts', 'TextCouple']))
        self.assertTrue(response.url.endswith(reverse('texts:list_text_couples')))
        self.assertTrue(RequestForModeration.objects.filter(object_id=TextCoupleCopy.objects.filter(
            parent=TextCouple.objects.filter(id=text_couple.id))))
        self.assertNotContains(response, 'Request for this text couple already exists', status_code=302)
        self.assertTrue(response.url.endswith(reverse('texts:list_text_couples')))

    def test_view_send_to_moderation_http_post_send_request_other_user(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        text_couple = create_valid_random_text_couple(user)
        new_client, new_user = get_client_and_user_of_create_random_user_and_login()
        new_response = new_client.post(reverse('moderation:send_to_moderation', args=[text_couple.id,
                                                                                      'texts', 'TextCouple']))
        self.assertEqual(new_response.status_code, 403)
        self.assertFalse(RequestForModeration.objects.filter(object_id=TextCoupleCopy.objects.filter(
            parent=TextCouple.objects.filter(id=text_couple.id))))

    def test_view_send_to_moderation_http_post_send_exists_request(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        text_couple = create_valid_random_text_couple(user)
        client.post(reverse('moderation:send_to_moderation', args=[text_couple.id, 'texts', 'TextCouple']))
        response = client.post(reverse('moderation:send_to_moderation', args=[text_couple.id, 'texts', 'TextCouple']))
        self.assertContains(response, 'Request for this text couple already exists')

    def test_view_send_to_moderation_http_post_send_request_with_nonexistent_advertising_class(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        text_couple = create_valid_random_text_couple(user)
        advertising_class = ''.join(random.sample('abcdefjk', 6))
        response = client.post(reverse('moderation:send_to_moderation', args=[text_couple.id, 'texts',
                                                                              advertising_class]))
        self.assertContains(response, 'No type of advertising %s' % advertising_class)

    def test_view_list_request_for_moderation_http_get_anonymous_user(self):
        response = Client().get(reverse('moderation:list_request_for_moderation'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(LOGIN_URL + '?next=' + reverse('moderation:list_request_for_moderation')))

    def test_view_list_request_for_moderation_http_post_anonymous_user(self):
        response = Client().post(reverse('moderation:list_request_for_moderation'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(LOGIN_URL + '?next=' + reverse('moderation:list_request_for_moderation')))

    def test_view_list_request_for_moderation_http_get_user(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        text_couple = create_valid_random_text_couple(user)
        client.post(reverse('moderation:send_to_moderation', args=[text_couple.id, 'texts', 'TextCouple']))
        response = client.get(reverse('moderation:list_request_for_moderation'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, text_couple.short)
        self.assertContains(response, 'Approval pending')

    def test_view_list_request_for_moderation_http_get_moderator(self):
        client, user = get_client_and_user_of_create_random_user_and_login()
        text_couple = create_valid_random_text_couple(user)
        client.post(reverse('moderation:send_to_moderation', args=[text_couple.id, 'texts', 'TextCouple']))
        group = create_group(MODERATORS_GROUP)
        client_moderator, user_moderator = get_client_and_user_of_create_random_user_and_login()
        user_moderator.groups.add(group)
        response = client_moderator.get(reverse('moderation:list_request_for_moderation'))
        self.assertContains(response, text_couple.short)
        self.assertNotContains(response, 'Approval pending')

    def test_view_list_request_for_moderation_http_get_visible_accepted(self):
        client, client_moderator, request, text_couple_copy = create_users_request_to_moderation_and_text_couple_copy()
        request.status = RequestForModeration.ACCEPTED
        request.save()
        response = client.get(reverse('moderation:list_request_for_moderation'))
        response_moderator = client_moderator.get(reverse('moderation:list_request_for_moderation'))
        self.assertContains(response, text_couple_copy.short)
        self.assertNotContains(response_moderator, text_couple_copy.short)

    def test_view_list_request_for_moderation_http_get_visible_denied(self):
        client, client_moderator, request, text_couple_copy = create_users_request_to_moderation_and_text_couple_copy()
        request.status = RequestForModeration.DENIED
        request.save()
        response = client.get(reverse('moderation:list_request_for_moderation'))
        response_moderator = client_moderator.get(reverse('moderation:list_request_for_moderation'))
        self.assertContains(response, text_couple_copy.short)
        self.assertNotContains(response_moderator, text_couple_copy.short)

    def test_view_list_request_for_moderation_http_get_canceled(self):
        client, client_moderator, request, text_couple_copy = create_users_request_to_moderation_and_text_couple_copy()
        request.status = RequestForModeration.CANCELED
        request.save()
        response = client.get(reverse('moderation:list_request_for_moderation'))
        response_moderator = client_moderator.get(reverse('moderation:list_request_for_moderation'))
        self.assertContains(response, text_couple_copy.short)
        self.assertNotContains(response_moderator, text_couple_copy.short)

    def test_view_list_request_for_moderation_http_get_link_to_moderation(self):
        client, client_moderator, request, text_couple_copy = create_users_request_to_moderation_and_text_couple_copy()
        response_moderator = client_moderator.get(reverse('moderation:list_request_for_moderation'))
        self.assertContains(response_moderator, '<a href="%s">Moderation</a>' %
                            (reverse('moderation:initiate_moderation', args=[request.id])))

    def test_view_moderation_http_get_anonymous_user(self):
        text_id = random.randint(1, 100)
        response = Client().get(reverse('moderation:initiate_moderation', args=[text_id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(LOGIN_URL + '?next=' +
                                              reverse('moderation:initiate_moderation', args=[text_id])))

    def test_view_moderation_http_get_no_user_group(self):
        client, client_moderator, request, text_couple_copy = create_users_request_to_moderation_and_text_couple_copy()
        response = client.get(reverse('moderation:initiate_moderation', args=[text_couple_copy.parent.id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(LOGIN_URL + '?next=' + reverse('moderation:initiate_moderation',
                                                                             args=[text_couple_copy.parent.id])))

    def test_view_moderation_http_get(self):
        client, client_moderator, request, text_couple_copy = create_users_request_to_moderation_and_text_couple_copy()
        response = client_moderator.get(reverse('moderation:initiate_moderation', args=[request.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        self.assertContains(response, 'csrfmiddlewaretoken')
        self.assertContains(response, '<input type="submit" value="OK">')
        self.assertTrue(RequestForModeration.objects.filter(id=request.id, status=RequestForModeration.IS_MODERATED)
                        .exists())

    def test_view_moderation_http_post(self):
        client, client_moderator, request, text_couple_copy = create_users_request_to_moderation_and_text_couple_copy()
        message = ''.join(random.sample('qwertyuiop', 10))
        response = client_moderator.post(reverse('moderation:initiate_moderation', args=[request.id]),
                                         {'status': RequestForModeration.DENIED, 'message_from_moderator': message})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(reverse('moderation:list_request_for_moderation')))
        self.assertTrue(RequestForModeration.objects.filter(id=request.id, status=RequestForModeration.DENIED,
                                                            message_from_moderator=message).exists())

    def test_view_moderation_http_post_message_from_moderator_blank(self):
        client, client_moderator, request, text_couple_copy = create_users_request_to_moderation_and_text_couple_copy()
        client_moderator.post(reverse('moderation:initiate_moderation', args=[request.id]),
                              {'status': RequestForModeration.DENIED, 'message_from_moderator': ""})
        self.assertFalse(RequestForModeration.objects.filter(id=request.id, status=RequestForModeration.DENIED)
                         .exists())


class FormTests(TestCase):
    def test_ModerationForm_with_status_accepted(self):
        self.assertTrue(ModerationForm({'status': RequestForModeration.ACCEPTED,
                                        'message_from_moderator': 'test'}).is_valid())

    def test_ModerationForm_with_status_denied(self):
        self.assertTrue(ModerationForm({'status': RequestForModeration.DENIED,
                                        'message_from_moderator': 'test'}).is_valid())

    def test_ModerationForm_with_status_incorrect(self):
        self.assertFalse(ModerationForm({'status': RequestForModeration.CANCELED,
                                        'message_from_moderator': 'test'}).is_valid())

    def test_ModerationForm_with_status_accepted_message_blank(self):
        self.assertTrue(ModerationForm({'status': RequestForModeration.ACCEPTED,
                                        'message_from_moderator': ''}).is_valid())

    def test_ModerationForm_with_status_denied_message_blank(self):
        self.assertFalse(ModerationForm({'status': RequestForModeration.DENIED,
                                        'message_from_moderator': ''}).is_valid())

    def test_ModerationForm_with_status_denied_message_len_equals_500(self):
        self.assertTrue(ModerationForm({'status': RequestForModeration.DENIED,
                                        'message_from_moderator': 'qwertyuiop'*50}).is_valid())

    def test_ModerationForm_with_status_denied_message_len_equals_501(self):
        self.assertFalse(ModerationForm({'status': RequestForModeration.DENIED,
                                        'message_from_moderator': 'qwertyuiop'*50 + "a"}).is_valid())


def create_user_and_request_for_moderation(status):
    username, password = create_two_random_text()
    user = User(username=username, password=password)
    user.save()
    text_couple = create_valid_random_text_couple(user)
    text_couple_copy = text_couple.create_copy()
    request_for_moderation = RequestForModeration(content_object=text_couple_copy, status=status)
    request_for_moderation.save()
    return user, request_for_moderation


class FunctionTests(TestCase):
    fixtures = ['initial_data.json', ]

    def test_begin_moderation_status_approval_pending(self):
        user, request_for_moderation = create_user_and_request_for_moderation(RequestForModeration.APPROVAL_PENDING)
        error = False
        try:
            begin_moderation(user, request_for_moderation)
        except ModerationError:
            error = True
        self.assertFalse(error)

    def test_begin_moderation_status_accepted(self):
        user, request_for_moderation = create_user_and_request_for_moderation(RequestForModeration.ACCEPTED)
        self.assertRaises(ModerationError, begin_moderation, user, request_for_moderation)

    def test_function_begin_moderation_status_denied(self):
        user, request_for_moderation = create_user_and_request_for_moderation(RequestForModeration.DENIED)
        self.assertRaises(ModerationError, begin_moderation, user, request_for_moderation)

    def test_function_begin_moderation_status_canceled(self):
        user, request_for_moderation = create_user_and_request_for_moderation(RequestForModeration.CANCELED)
        self.assertRaises(ModerationError, begin_moderation, user, request_for_moderation)

    def test_function_begin_moderation_status_is_moderated(self):
        user, request_for_moderation = create_user_and_request_for_moderation(RequestForModeration.IS_MODERATED)
        self.assertRaises(ModerationError, begin_moderation, user, request_for_moderation)

    def test_function_begin_moderation_status_is_moderated_moderator_user(self):
        user, request_for_moderation = create_user_and_request_for_moderation(RequestForModeration.IS_MODERATED)
        request_for_moderation.moderator = user
        error = False
        try:
            begin_moderation(user, request_for_moderation)
        except ModerationError:
            error = True
        self.assertFalse(error)

    def test_function_moderation_status_accepted(self):
        user, request_for_moderation = create_user_and_request_for_moderation(RequestForModeration.APPROVAL_PENDING)
        message = ''.join(random.sample('abcdefjk', 8))
        moderation(user, request_for_moderation, RequestForModeration.ACCEPTED, message)
        self.assertEquals(request_for_moderation.status, RequestForModeration.ACCEPTED)
        self.assertEquals(request_for_moderation.message_from_moderator, message)
        self.assertEquals(request_for_moderation.moderator, user)

    def test_function_moderation_status_denied(self):
        user, request_for_moderation = create_user_and_request_for_moderation(RequestForModeration.APPROVAL_PENDING)
        message = ''.join(random.sample('abcdefjk', 8))
        moderation(user, request_for_moderation, RequestForModeration.DENIED, message)
        self.assertEquals(request_for_moderation.status, RequestForModeration.DENIED)
        self.assertEquals(request_for_moderation.message_from_moderator, message)
        self.assertEquals(request_for_moderation.moderator, user)

    def test_function_moderation_status_approval_pending(self):
        user, request_for_moderation = create_user_and_request_for_moderation(RequestForModeration.APPROVAL_PENDING)
        message = ''.join(random.sample('abcdefjk', 8))
        self.assertRaises(ModerationError, moderation, user, request_for_moderation,
                          RequestForModeration.APPROVAL_PENDING, message)

    def test_function_moderation_status_canceled(self):
        user, request_for_moderation = create_user_and_request_for_moderation(RequestForModeration.APPROVAL_PENDING)
        message = ''.join(random.sample('abcdefjk', 8))
        self.assertRaises(ModerationError, moderation, user, request_for_moderation, RequestForModeration.CANCELED,
                          message)

    def test_function_moderation_status_is_moderated(self):
        user, request_for_moderation = create_user_and_request_for_moderation(RequestForModeration.APPROVAL_PENDING)
        message = ''.join(random.sample('abcdefjk', 8))
        self.assertRaises(ModerationError, moderation, user, request_for_moderation, RequestForModeration.IS_MODERATED,
                          message)

    def test_function_get_user_group(self):
        add_group = create_group(''.join(random.sample('abcdefjk', 8)))
        client, user = get_client_and_user_of_create_random_user_and_login()
        user.groups.add(add_group)
        group = get_user_group(user)
        self.assertIn(add_group, group)


class FixturesTests(TestCase):
    fixtures = ['initial_data.json', ]

    def test_fixtures_group_contains_moderator(self):
        group = Group.objects.filter(name=MODERATORS_GROUP)
        self.assertTrue(group)
