from django.test import TestCase
from django.urls import reverse
from .models import ContactMessage


class ContactModelTest(TestCase):
    def test_contact_message_string_representation(self):
        msg = ContactMessage.objects.create(
            fullname='Alice',
            email='alice@example.com',
            phone='1234567890',
            message='Hello BookMyTable',
        )
        self.assertEqual(str(msg), 'Message from Alice')


class ContactViewsTest(TestCase):
    def test_contact_page_loads(self):
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact/contact.html')

    def test_contact_form_valid_submission(self):
        response = self.client.post(reverse('contact'), {
            'fullname': 'Alice',
            'email': 'alice@example.com',
            'phone': '1234567890',
            'message': 'I would like to reserve a table for 4 people.',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_contact_form_invalid_email(self):
        response = self.client.post(reverse('contact'), {
            'fullname': 'Alice',
            'email': 'not-an-email',
            'phone': '1234567890',
            'message': 'Hello',
        })
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertContains(response, 'Enter a valid email address.')

    def test_contact_form_message_too_long(self):
        response = self.client.post(reverse('contact'), {
            'fullname': 'Alice',
            'email': 'alice@example.com',
            'phone': '1234567890',
            'message': 'x' * 501,
        })
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertContains(response, 'cannot be longer')

    def test_contact_form_missing_required_fields(self):
        response = self.client.post(reverse('contact'), {
            'fullname': '',
            'email': '',
            'phone': '',
            'message': '',
        })
        self.assertEqual(ContactMessage.objects.count(), 0)
