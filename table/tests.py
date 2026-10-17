from django.test import TestCase
from django.urls import reverse
from .models import Table


class TableModelTest(TestCase):
    def test_table_string_representation(self):
        table = Table.objects.create(number=1, seats=6)
        self.assertEqual(str(table), 'Table 1')

    def test_table_default_seats(self):
        table = Table.objects.create(number=2)
        self.assertEqual(table.seats, 6)

    def test_table_fields(self):
        table = Table.objects.create(number=3, seats=8)
        self.assertEqual(table.number, 3)
        self.assertEqual(table.seats, 8)


class TableViewsTest(TestCase):
    def setUp(self):
        Table.objects.create(number=1, seats=4)
        Table.objects.create(number=2, seats=8)

    def test_table_list_view(self):
        response = self.client.get(reverse('table_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'table/table_list.html')
        self.assertContains(response, 'Table 1')
        self.assertContains(response, 'Table 2')
