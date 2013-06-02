from django.core.urlresolvers import reverse
from django.test import TestCase


class ViewTests(TestCase):
    def test_purchase_required_login(self):
        url = reverse('attendees_purchase')
        self.assertRedirects(
            self.client.get(url), '/accounts/login/?next=' + url)

    def test_purchase_confirm_required_login(self):
        url = reverse('attendees_purchase_confirm', kwargs={'pk': 123})
        self.assertRedirects(
            self.client.get(url), '/accounts/login/?next=' + url)

    def test_purchase_names_required_login(self):
        url = reverse('attendees_purchase_names', kwargs={'pk': 123})
        self.assertRedirects(
            self.client.get(url), '/accounts/login/?next=' + url)
