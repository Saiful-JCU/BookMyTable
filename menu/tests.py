from django.test import TestCase
from django.urls import reverse
from .models import MenuCategory, MenuItem


class MenuModelTest(TestCase):
    def setUp(self):
        self.category = MenuCategory.objects.create(name='Starters')
        self.item = MenuItem.objects.create(
            category=self.category,
            name='Garlic Bread',
            description='Toasted bread with garlic butter.',
            price=5.99,
        )

    def test_category_string_representation(self):
        self.assertEqual(str(self.category), 'Starters')

    def test_menu_item_string_representation(self):
        self.assertEqual(str(self.item), 'Garlic Bread')

    def test_menu_item_belongs_to_category(self):
        self.assertEqual(self.item.category, self.category)

    def test_menu_item_price(self):
        self.assertEqual(float(self.item.price), 5.99)


class MenuViewsTest(TestCase):
    def setUp(self):
        category = MenuCategory.objects.create(name='Starters')
        MenuItem.objects.create(
            category=category,
            name='Garlic Bread',
            description='Toasted bread with garlic butter.',
            price=5.99,
        )

    def test_menu_list_view(self):
        response = self.client.get(reverse('menu_item_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'menu/menu_item_list.html')
        self.assertContains(response, 'Garlic Bread')
        self.assertContains(response, 'Starters')
