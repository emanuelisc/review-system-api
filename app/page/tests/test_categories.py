from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import PageCategory, Page

from page.serializers import PageCategorySerializer


CATEGORIES_URL = reverse('page:admincat-list')
CATEGORIESLIST_URL = reverse('page:categories-list')


def sample_category(name='Naujiena'):
    # Create and return a sample category
    return PageCategory.objects.create(name=name)


def detail_url(category_id):
    # Return recipe detail URL
    return reverse('page:admincat-detail', args=[category_id])


def detail_public_url(category_id):
    # Return recipe detail URL
    return reverse('page:categories-detail', args=[category_id])


class PublicCategoryApiTests(TestCase):
    # Test the publicly available categories API

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_category_list(self):
        # Test retrieving a list of categories
        PageCategory.objects.create(name='Puslapis')
        PageCategory.objects.create(name='Naujiena')

        res = self.client.get(CATEGORIESLIST_URL)

        categories = PageCategory.objects.all().order_by('-name')
        serializer = PageCategorySerializer(categories, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_category_public_unsuccessfull(self):
        """ Test create a new category for unauthorized on public end """
        payload = {'name': 'Naujiena'}
        res = self.client.post(CATEGORIESLIST_URL, payload)

        exists = PageCategory.objects.filter(
            name=payload['name'],
        ).exists()
        self.assertFalse(exists)
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_category_unsuccessfull(self):
        """ Test create a new category for unauthorized """
        payload = {'name': 'Naujiena'}
        res = self.client.post(CATEGORIES_URL, payload)

        exists = PageCategory.objects.filter(
            name=payload['name'],
        ).exists()
        self.assertFalse(exists)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_category_details(self):
        """ Test category details public """
        payload = {'name': 'Naujiena'}
        category = sample_category()
        exists = PageCategory.objects.filter(name=payload['name'],).exists()
        self.assertTrue(exists)

        url = detail_public_url(category.id)
        res = self.client.get(url)
        serializer = PageCategorySerializer(category)

        self.assertEqual(res.data, serializer.data)

    def test_category_delete(self):
        """ Test category delete public """
        payload = {'name': 'Naujiena'}
        category = sample_category()
        exists = PageCategory.objects.filter(name=payload['name'],).exists()
        self.assertTrue(exists)

        url = detail_url(category.id)
        res = self.client.get(url)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAdminCategoryApiTests(TestCase):
    # Test the private categories API

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'testpass'
        )
        self.user.is_staff = True
        self.client.force_authenticate(self.user)

    def test_create_category_successfull(self):
        """ Test create a new category """
        payload = {'name': 'Naujiena'}
        self.client.post(CATEGORIES_URL, payload)

        exists = PageCategory.objects.filter(name=payload['name'],).exists()
        self.assertTrue(exists)

    def test_category_details(self):
        """ Test category details """
        payload = {'name': 'Naujiena'}
        category = sample_category()
        exists = PageCategory.objects.filter(name=payload['name'],).exists()
        self.assertTrue(exists)

        url = detail_url(category.id)
        res = self.client.get(url)
        serializer = PageCategorySerializer(category)

        self.assertEqual(res.data, serializer.data)

    def test_category_delete(self):
        """ Test category delete """
        payload = {'name': 'Naujiena'}
        category = sample_category()
        exists = PageCategory.objects.filter(name=payload['name'],).exists()
        self.assertTrue(exists)

        url = detail_url(category.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_category_invalid(self):
        # Test creating invalid category fails
        payload = {'name': ''}
        res = self.client.post(CATEGORIES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_categories_assigned_to_pages(self):
        # Test filtering categories by those assigned to pages
        category1 = PageCategory.objects.create(name='Puslapis')
        category2 = PageCategory.objects.create(name='Naujiena')
        page = Page.objects.create(
            title='Apple crumble',
            text='Lorem ipsum'
        )
        page.categories.add(category1)

        res = self.client.get(CATEGORIES_URL, {'assigned_only': 1})

        serializer1 = PageCategorySerializer(category1)
        serializer2 = PageCategorySerializer(category2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_categories_assigned_unique(self):
        # Test filtering categories by assigned return unique items
        category = PageCategory.objects.create(name='Puslapis')
        PageCategory.objects.create(name='Naujiena')
        page1 = Page.objects.create(
            title='Text 2',
            text='30'
        )
        page1.categories.add(category)
        page2 = Page.objects.create(
            title='Coriander eggs on toast',
            text='Lorem ipsum'
        )
        page2.categories.add(category)

        res = self.client.get(CATEGORIES_URL, {'assigned_only': 1})
        self.assertEqual(len(res.data), 1)
