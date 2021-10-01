from django.test import TestCase
from django.urls import reverse


class Tests(TestCase):
    fixtures = ["initial_data"]

    def test_view_with_no_args(self):
        response = self.client.get(reverse("salesreporting", args=0), {}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("admin/stregsystem/report/sales.html")

    def test_all_ok(self):
        self.client.login(username="tester", password="treotreo")
        response = self.client.post(
            reverse("salesreporting"),
            {"products": "1", "from_date": "2007-07-01", "to_date": "2007-07-30"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("admin/stregsystem/report/sales.html")
        self.assertSequenceEqual(response.context["sales"], [('', 'TOTAL', 0, '0.00')])

    def test_invalid_products(self):
        self.client.login(username="tester", password="treotreo")
        response = self.client.post(
            reverse("salesreporting"),
            {"products": "abe", "from_date": "2007-07-01", "to_date": "2007-07-30"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("admin/stregsystem/report/error_invalidsalefetch.html")

    def test_invalid_date_format(self):
        self.client.login(username="tester", password="treotreo")
        response = self.client.get(
            reverse("salesreporting"),
            {
                "products": "1",
                "from_date": "2007-30-07",
                "to_date": "2007-07-30",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("admin/stregsystem/report/sales.html")
