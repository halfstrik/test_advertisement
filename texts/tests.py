from django.test import TestCase

from texts.models import TextCouple


class TextCoupleTests(TestCase):
    def test__str__return_short_part(self):
        text_couple = TextCouple(short='short part', long='long part')
        self.assertEquals('short part (long pa...)', str(text_couple))
