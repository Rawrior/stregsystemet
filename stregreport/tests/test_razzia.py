from django.test import TestCase
from django.urls import reverse
from stregreport.models import BreadRazzia


class GeneralTests(TestCase):
    fixtures = ["initial_data"]

    def test_registered_member_is_in_member_list(self):
        self.client.login(username="tester", password="treotreo")
        response = self.client.get(reverse("razzia_new_BR"), follow=True)
        razzia_url, _ = response.redirect_chain[-1]

        response_add = self.client.post(
            razzia_url, {"username": "jokke"}, follow=True)

        response_members = self.client.get(razzia_url + "members", follow=True)

        self.assertEqual(response_add.status_code, 200)
        self.assertTemplateUsed(
            response_members, "admin/stregsystem/razzia/members.html")
        self.assertContains(response_members, "jokke", status_code=200)


class BreadTests(TestCase):
    fixtures = ["initial_data"]

    def test_can_create_new(self):
        previous_number_razzias = BreadRazzia.objects.filter(
            razzia_type=BreadRazzia.BREAD).count()

        self.client.login(username="tester", password="treotreo")
        response = self.client.get(reverse("razzia_new_BR"), follow=True)
        last_url, status_code = response.redirect_chain[-1]

        current_number_razzias = BreadRazzia.objects.filter(
            razzia_type=BreadRazzia.BREAD).count()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "admin/stregsystem/razzia/bread.html")
        self.assertEqual(current_number_razzias, previous_number_razzias + 1)

    def test_member_can_only_register_once(self):
        self.client.login(username="tester", password="treotreo")
        response = self.client.get(reverse("razzia_new_BR"), follow=True)
        razzia_url, _ = response.redirect_chain[-1]

        response_add_1 = self.client.post(
            razzia_url, {"username": "jokke"}, follow=True)

        response_add_2 = self.client.post(
            razzia_url, {"username": "jokke"}, follow=True)

        self.assertEqual(response_add_1.status_code, 200)
        self.assertEqual(response_add_2.status_code, 200)
        self.assertTemplateUsed(
            response, "admin/stregsystem/razzia/bread.html")
        self.assertNotContains(
            response_add_1, "already checked in", status_code=200)
        self.assertContains(
            response_add_2, "already checked in", status_code=200)


class FoobarTests(TestCase):
    fixtures = ["initial_data"]

    def test_can_create_new(self):
        previous_number_razzias = BreadRazzia.objects.filter(
            razzia_type=BreadRazzia.FOOBAR).count()

        self.client.login(username="tester", password="treotreo")
        response = self.client.get(reverse("razzia_new_FB"), follow=True)
        last_url, status_code = response.redirect_chain[-1]

        current_number_razzias = BreadRazzia.objects.filter(
            razzia_type=BreadRazzia.FOOBAR).count()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "admin/stregsystem/razzia/foobar.html")
        self.assertEqual(current_number_razzias, previous_number_razzias + 1)

    def test_member_can_register_multiple_times(self):
        self.client.login(username="tester", password="treotreo")
        response = self.client.get(reverse("razzia_new_FB"), follow=True)
        razzia_url, _ = response.redirect_chain[-1]

        response_members_0 = self.client.get(
            razzia_url + "members", follow=True)

        response_add_1 = self.client.post(
            razzia_url, {"username": "jokke"}, follow=True)

        response_add_2 = self.client.post(
            razzia_url, {"username": "jokke"}, follow=True)

        response_members_2 = self.client.get(
            razzia_url + "members", follow=True)

        self.assertEqual(response_add_1.status_code, 200)
        self.assertEqual(response_add_2.status_code, 200)
        self.assertTemplateUsed(
            response_add_1, "admin/stregsystem/razzia/foobar.html")
        self.assertTemplateUsed(
            response_add_2, "admin/stregsystem/razzia/foobar.html")
        self.assertNotContains(
            response_add_1, "last checked in at", status_code=200)
        self.assertContains(
            response_add_2, "last checked in at", status_code=200)
        self.assertContains(response_members_0, "0 fember(s)", status_code=200)
        self.assertContains(response_members_2, "2 fember(s)", status_code=200)
