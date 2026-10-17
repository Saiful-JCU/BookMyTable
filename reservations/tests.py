from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Reservation
from table.models import Table


class ReservationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='pass12345')
        self.table = Table.objects.create(number=1, seats=4)

    def test_reservation_string_representation(self):
        reservation = Reservation.objects.create(
            user=self.user,
            full_name='Alice Smith',
            email='alice@example.com',
            phone='1234567890',
            reservation_date='2026-11-01',
            reservation_time='19:00:00',
            number_of_people=2,
            table=self.table,
        )
        self.assertEqual(
            str(reservation),
            'Reservation by Alice Smith on 2026-11-01 at 19:00:00',
        )


class ReservationViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='pass12345')
        self.client.login(username='alice', password='pass12345')
        self.table = Table.objects.create(number=1, seats=4)

    def _valid_post_data(self, **overrides):
        data = {
            'full_name': 'Alice Smith',
            'email': 'alice@example.com',
            'phone': '1234567890',
            'reservation_date': '2026-11-01',
            'reservation_time': '19:00',
            'number_of_people': '2',
            'special_requests': '',
            'table': str(self.table.pk),
        }
        data.update(overrides)
        return data

    def _create_reservation(self, **overrides):
        defaults = {
            'user': self.user,
            'full_name': 'Alice Smith',
            'email': 'alice@example.com',
            'phone': '1234567890',
            'reservation_date': '2026-11-01',
            'reservation_time': '19:00:00',
            'number_of_people': 2,
            'table': self.table,
        }
        defaults.update(overrides)
        return Reservation.objects.create(**defaults)

    def test_reservation_list_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('reservations:reservation_list'))
        self.assertEqual(response.status_code, 302)

    def test_reserve_table_page_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('reservations:reserve_table'))
        self.assertEqual(response.status_code, 302)

    def test_reservation_list_displays_reservations(self):
        self._create_reservation()
        response = self.client.get(reverse('reservations:reservation_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reservations/reservation_list.html')
        self.assertContains(response, 'Alice Smith')

    def test_reservation_list_shows_empty_message(self):
        response = self.client.get(reverse('reservations:reservation_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No reservations available.')

    def test_reserve_table_page_get(self):
        response = self.client.get(reverse('reservations:reserve_table'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reservations/reserve_table.html')

    def test_reserve_table_valid_submission(self):
        response = self.client.post(
            reverse('reservations:reserve_table'), self._valid_post_data()
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Reservation.objects.count(), 1)

    def test_reserve_table_duplicate_date_rejected(self):
        self.client.post(reverse('reservations:reserve_table'), self._valid_post_data())
        response = self.client.post(
            reverse('reservations:reserve_table'), self._valid_post_data()
        )
        self.assertEqual(Reservation.objects.count(), 1)
        self.assertContains(response, 'You already have a reservation on this date.')

    def test_reserve_table_capacity_exceeded(self):
        response = self.client.post(
            reverse('reservations:reserve_table'),
            self._valid_post_data(number_of_people='61'),
        )
        self.assertEqual(Reservation.objects.count(), 0)
        self.assertContains(response, 'Number of People must be between 1 and 60.')

    def test_reserve_table_time_outside_operating_hours(self):
        response = self.client.post(
            reverse('reservations:reserve_table'),
            self._valid_post_data(reservation_time='22:00'),
        )
        self.assertEqual(Reservation.objects.count(), 0)
        self.assertContains(response, 'between 08:00 and 21:00')

    def test_reserve_table_missing_required_fields(self):
        response = self.client.post(reverse('reservations:reserve_table'), {})
        self.assertEqual(Reservation.objects.count(), 0)
        self.assertContains(response, 'Full Name is required.')

    def test_reserve_table_missing_table_selection(self):
        response = self.client.post(
            reverse('reservations:reserve_table'),
            self._valid_post_data(table=''),
        )
        self.assertEqual(Reservation.objects.count(), 0)
        self.assertContains(response, 'Table selection is required.')

    def test_edit_reservation_updates_data(self):
        reservation = self._create_reservation()
        response = self.client.post(
            reverse('reservations:edit_reservation', args=[reservation.pk]),
            self._valid_post_data(number_of_people='4'),
        )
        self.assertEqual(response.status_code, 302)
        reservation.refresh_from_db()
        self.assertEqual(reservation.number_of_people, 4)

    def test_delete_reservation(self):
        reservation = self._create_reservation()
        response = self.client.post(
            reverse('reservations:delete_reservation', args=[reservation.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Reservation.objects.count(), 0)
