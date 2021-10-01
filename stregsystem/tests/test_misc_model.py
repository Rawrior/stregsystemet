from django.test import TestCase
from stregsystem.models import active_str, price_display


class Tests(TestCase):
    def test_price_display_none(self):
        v = price_display(None)
        self.assertEqual(v, "0.00 kr.")

    def test_price_display_zero(self):
        v = price_display(0)
        self.assertEqual(v, "0.00 kr.")

    def test_price_display_one(self):
        v = price_display(1)
        self.assertEqual(v, "0.01 kr.")

    def test_price_display_hundred(self):
        v = price_display(100)
        self.assertEqual(v, "1.00 kr.")

    def test_active_str_true(self):
        v = active_str(True)
        self.assertEqual(v, "+")

    def test_active_str_false(self):
        v = active_str(False)
        self.assertEqual(v, "-")
