import pytz
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from stregsystem import views as stregsystem_views
from django.utils import timezone
from freezegun import freeze_time
from stregsystem.models import (
    Member,
    PayTransaction,
    Product,
    Sale
)
from decorators import suppress_request_warnings


def assertCountEqual(case, *args, **kwargs):
    try:
        case.assertCountEqual(*args, **kwargs)
    except AttributeError:
        case.assertItemsEqual(*args, **kwargs)


class Tests(TestCase):
    fixtures = ["initial_data"]

    def test_make_sale_letter_quickbuy(self):
        response = self.client.post(reverse('quickbuy', args="1"), {
                                    "quickbuy": "jokke a"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("stregsystem/error_invalidquickbuy.html")

    @patch('stregsystem.models.Member.can_fulfill')
    @patch('stregsystem.models.Member.fulfill')
    def test_make_sale_quickbuy_success(self, fulfill, can_fulfill):
        can_fulfill.return_value = True

        response = self.client.post(reverse('quickbuy', args=(1,)), {
                                    "quickbuy": "jokke 1"})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "stregsystem/index_sale.html")

        assertCountEqual(self, response.context["products"], {
                         Product.objects.get(id=1)})
        self.assertEqual(
            response.context["member"], Member.objects.get(username="jokke"))

        fulfill.assert_called_once_with(PayTransaction(900))

    @suppress_request_warnings
    def test_make_sale_quickbuy_fail(self):
        member_username = 'jan'
        member_before = Member.objects.get(username=member_username)
        response = self.client.post(reverse('quickbuy', args=(1,)), {
                                    "quickbuy": member_username + " 1"})
        member_after = Member.objects.get(username=member_username)

        self.assertEqual(response.status_code, 402)
        self.assertTemplateUsed(response, "stregsystem/error_stregforbud.html")
        self.assertEqual(member_before.balance, member_after.balance)

        self.assertEqual(response.context["member"], Member.objects.get(
            username=member_username))

    def test_make_sale_quickbuy_wrong_product(self):
        response = self.client.post(reverse('quickbuy', args=(1,)), {
                                    "quickbuy": "jokke 99"})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "stregsystem/error_productdoesntexist.html")

    @patch('stregsystem.models.Member.can_fulfill')
    def test_make_sale_menusale_fail(self, can_fulfill):
        can_fulfill.return_value = False
        member_id = 1
        member_before = Member.objects.get(id=member_id)

        response = self.client.post(
            reverse('menu', args=(1, member_id)), data={'product_id': 1})

        member_after = Member.objects.get(id=member_id)

        self.assertEqual(member_before.balance, member_after.balance)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "stregsystem/error_stregforbud.html")
        self.assertEqual(response.context["member"], Member.objects.get(id=1))

    @patch('stregsystem.models.Member.can_fulfill')
    @patch('stregsystem.models.Member.fulfill')
    def test_make_sale_menusale_success(self, fulfill, can_fulfill):
        can_fulfill.return_value = True

        response = self.client.post(
            reverse('menu', args=(1, 1)), data={'product_id': 1})
        self.assertTemplateUsed(response, "stregsystem/menu.html")

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context["bought"], Product.objects.get(id=1))
        self.assertEqual(response.context["member"], Member.objects.get(id=1))

        fulfill.assert_called_once_with(PayTransaction(900))

    def test_quicksale_has_status_line(self):
        response = self.client.post(reverse('quickbuy', args=(1,)), {
                                    "quickbuy": "jokke 1"})

        self.assertContains(
            response,
            "<b><span class=\"username\">jokke</span> har lige købt Limfjordsporter for tilsammen " "9.00 kr.</b>",
            html=True,
        )

    def test_usermenu(self):
        response = self.client.post(
            reverse('quickbuy', args=(1,)), {"quickbuy": "jokke"})

        self.assertTemplateUsed(response, "stregsystem/menu.html")

    def test_quickbuy_empty(self):
        response = self.client.post(
            reverse('quickbuy', args=(1,)), {"quickbuy": ""})

        self.assertTemplateUsed(response, "stregsystem/index.html")

    def test_index(self):
        response = self.client.post(reverse('index'))

        # Assert permanent redirect
        self.assertEqual(response.status_code, 301)

    def test_menu_index(self):
        response = self.client.post(reverse('menu_index', args=(1,)))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "stregsystem/index.html")
        # Assert that the index screen at least contains one of the products in
        # the database. Technically this doesn't check everything exhaustively,
        # but it's better than nothing -Jesper 18/09-2017
        self.assertContains(response, "<td>Limfjordsporter</td>", html=True)

    def test_quickbuy_no_known_member(self):
        response = self.client.post(reverse('quickbuy', args=(1,)), {
                                    "quickbuy": "notinthere"})

        self.assertTemplateUsed(
            response, "stregsystem/error_usernotfound.html")

    def test_quicksale_increases_bought(self):
        before = Product.objects.get(id=2)
        before_bought = before.bought
        before_member = Member.objects.get(username="jokke")

        response = self.client.post(reverse('quickbuy', args=(1,)), {
                                    "quickbuy": "jokke 2"})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "stregsystem/index_sale.html")

        after = Product.objects.get(id=2)
        after_member = Member.objects.get(username="jokke")

        self.assertEqual(before_bought + 1, after.bought)
        # 900 is the product price
        self.assertEqual(before_member.balance - 900, after_member.balance)

    def test_quicksale_quanitity_none_noincrease(self):
        before = Product.objects.get(id=1)
        before_member = Member.objects.get(username="jokke")

        response = self.client.post(reverse('quickbuy', args=(1,)), {
                                    "quickbuy": "jokke 1"})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "stregsystem/index_sale.html")

        after = Product.objects.get(id=1)
        after_member = Member.objects.get(username="jokke")

        self.assertEqual(before.bought, after.bought)
        # 900 is the product price
        self.assertEqual(before_member.balance - 900, after_member.balance)

    def test_quicksale_out_of_stock(self):
        before = Product.objects.get(id=1)
        before_member = Member.objects.get(username="jokke")

        response = self.client.post(reverse('quickbuy', args=(1,)), {
                                    "quickbuy": "jokke 3"})

        self.assertEqual(response.status_code, 200)
        # I don't know which template to use (I should probably make one). So
        # for now let's just make sure that we at least don't use the one that
        # says "correct" - Jesper 14/09-2017
        self.assertTemplateNotUsed(response, "stregsystem/index_sale.html")

        after = Product.objects.get(id=1)
        after_member = Member.objects.get(username="jokke")

        self.assertEqual(before.bought, after.bought)
        self.assertEqual(before_member.balance, after_member.balance)

    def test_quicksale_product_not_in_room(self):
        before_product = Product.objects.get(id=4)
        before_member = Member.objects.get(username="jokke")

        response = self.client.post(reverse('quickbuy', args=(1,)), {
                                    "quickbuy": "jokke 4"})

        after_product = Product.objects.get(id=4)
        after_member = Member.objects.get(username="jokke")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "stregsystem/error_productdoesntexist.html")

        self.assertEqual(before_product.bought, after_product.bought)
        self.assertEqual(before_member.balance, after_member.balance)

    def test_quicksale_product_available_all_rooms(self):
        before_product = Product.objects.get(id=1)
        before_member = Member.objects.get(username="jokke")

        response = self.client.post(reverse('quickbuy', args=(1,)), {
                                    "quickbuy": "jokke 1"})

        after_product = Product.objects.get(id=1)
        after_member = Member.objects.get(username="jokke")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "stregsystem/index_sale.html")

        self.assertEqual(before_member.balance - 900, after_member.balance)

    def test_menusale_product_not_in_room(self):
        before_product = Product.objects.get(id=4)
        before_member = Member.objects.get(username="jokke")

        response = self.client.post(reverse('menu', args=(
            1, before_member.id)), data={'product_id': 4})

        after_product = Product.objects.get(id=4)
        after_member = Member.objects.get(username="jokke")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "stregsystem/menu.html")

        self.assertEqual(before_product.bought, after_product.bought)
        self.assertEqual(before_member.balance, after_member.balance)

    def test_multibuy_hint_not_applicable(self):
        member = Member.objects.get(username="jokke")
        give_multibuy_hint, sale_hints = stregsystem_views._multibuy_hint(
            timezone.now(), member)
        self.assertFalse(give_multibuy_hint)
        self.assertIsNone(sale_hints)

    def test_multibuy_hint_one_buy_not_applicable(self):
        member = Member.objects.get(username="jokke")
        coke = Product.objects.create(name="coke", price=100, active=True)
        Sale.objects.create(
            member=member,
            product=coke,
            price=100,
        )
        give_multibuy_hint, sale_hints = stregsystem_views._multibuy_hint(
            timezone.now(), member)
        self.assertFalse(give_multibuy_hint)
        self.assertIsNone(sale_hints)

    def test_multibuy_hint_two_buys_applicable(self):
        member = Member.objects.get(username="jokke")
        coke = Product.objects.create(name="coke", price=100, active=True)
        with freeze_time(timezone.datetime(2018, 1, 1)) as frozen_time:
            for i in range(1, 3):
                Sale.objects.create(
                    member=member,
                    product=coke,
                    price=100,
                )
                frozen_time.tick()
        give_multibuy_hint, sale_hints = stregsystem_views._multibuy_hint(
            timezone.datetime(2018, 1, 1, tzinfo=pytz.UTC), member
        )
        self.assertTrue(give_multibuy_hint)
        self.assertEqual(sale_hints, "{} {}:{}".format(
            "<span class=\"username\">jokke</span>", coke.id, 2))
