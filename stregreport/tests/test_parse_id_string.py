from django.test import TestCase
from stregreport import views


class Tests(TestCase):
    def test_success(self):
        id_string = "11 13 14 1839"
        res = views.parse_id_string(id_string)

        self.assertSequenceEqual([11, 13, 14, 1839], res)

    def test_fail(self):
        wrong_id_string = "0x10 abe 10"
        with self.assertRaises(RuntimeError):
            views.parse_id_string(wrong_id_string)

    def test_unicode_success(self):
        id_string_unicode = u"11 13"
        res = views.parse_id_string(id_string_unicode)

        self.assertSequenceEqual([11, 13], res)
