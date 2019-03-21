import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Page, PageCategory

from page.serializers import PageSerializer, PageDetailSerializer


ADMIN_PAGES_URL = reverse('page:adminpages-list')
PAGES_URL = reverse('page:pages-list')


def image_upload_url(page_id):
    # Return URL for page image upload
    return reverse('page:adminpages-upload-image', args=[page_id])


def detail_url(page_id):
    # Return page detail URL
    return reverse('page:adminpages-detail', args=[page_id])


def detail_public_url(page_id):
    # Return page detail URL
    return reverse('page:pages-detail', args=[page_id])


def sample_category(name='Puslapis'):
    # Create and return a sample category
    return PageCategory.objects.create(name=name)


def sample_page(**params):
    # Create and return a sample page
    defaults = {
        'title': 'Sample page',
        'text': 'Lorem ipsum'
    }
    defaults.update(params)

    return Page.objects.create(**defaults)


class PublicPageApiTests(TestCase):
    """ Test unauthenticated page API access """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        # Test that authentication ir required
        sample_page()
        res = self.client.get(PAGES_URL)

        pages = Page.objects.all().order_by('-id')
        serializer = PageSerializer(pages, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_auth_required_unsuccessful(self):
        # Test that authentication is required but unsuccessful

        sample_page()
        res = self.client.get(ADMIN_PAGES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_view_page_detail(self):
        """ Test viewing a page details """
        page = sample_page()
        page.categories.add(sample_category())

        url = detail_public_url(page.id)
        res = self.client.get(url)

        serializer = PageDetailSerializer(page)
        self.assertEqual(res.data, serializer.data)

    def test_filter_pages_by_categories(self):
        """ Test returning pages with specific category """
        page1 = sample_page(title='Page 1')
        page2 = sample_page(title='Page 2')
        category1 = sample_category(name='Puslapis')
        category2 = sample_category(name='Naujiena')
        page1.categories.add(category1)
        page2.categories.add(category2)
        page3 = sample_page(title='Page 3')

        res = self.client.get(
            PAGES_URL,
            {'categories': f'{category1.id},{category2.id}'}
        )

        serializer1 = PageSerializer(page1)
        serializer2 = PageSerializer(page2)
        serializer3 = PageSerializer(page3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_partial_update_page(self):
        """ Test updating a page with patch """
        page = sample_page()
        page.categories.add(sample_category())
        new_category = sample_category(name='Naujiena')

        payload = {'title': 'Page 1', 'categories': [new_category.id]}
        url = detail_public_url(page.id)
        self.client.patch(url, payload)

        page.refresh_from_db()
        self.assertNotEqual(page.title, payload['title'])


class PrivatePageApiTests(TestCase):
    # Test unauthenticated page API access

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'testpass'
        )
        self.user.is_staff = True
        self.client.force_authenticate(self.user)

    def test_retrieve_pages(self):
        """ Test retrieving a list of pages for admin """
        sample_page(title='Page 1')

        res = self.client.get(ADMIN_PAGES_URL)

        pages = Page.objects.all().order_by('-id')
        serializer = PageSerializer(pages, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(len(serializer.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_page_detail(self):
        """ Test viewing a page details for admin """
        page = sample_page()
        page.categories.add(sample_category())

        url = detail_url(page.id)
        res = self.client.get(url)

        serializer = PageDetailSerializer(page)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_page(self):
        """ Test creating page """
        payload = {
            'title': 'Puslapis 1',
            'text': 'Lorem ipsum'
        }
        res = self.client.post(ADMIN_PAGES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        page = Page.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(page, key))

    def test_create_page_with_category(self):
        """ Test creating page with categories """
        category1 = sample_category(name='Puslapis')
        category2 = sample_category(name='Naujiena')
        payload = {
            'title': 'Puslapis 1',
            'categories': [category1.id, category2.id],
            'text': 'Lorem lipsum',
            'slug': 'puslapis-1'
        }
        res = self.client.post(ADMIN_PAGES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        page = Page.objects.get(id=res.data['id'])
        categories = page.categories.all()
        self.assertEqual(categories.count(), 2)
        self.assertIn(category1, categories)
        self.assertIn(category2, categories)

    def test_partial_update_page(self):
        """ Test updating a page with patch for admin """
        page = sample_page()
        page.categories.add(sample_category())
        new_category = sample_category(name='Naujiena')

        payload = {'title': 'Page 1', 'categories': [new_category.id]}
        url = detail_url(page.id)
        self.client.patch(url, payload)

        page.refresh_from_db()
        self.assertEqual(page.title, payload['title'])
        categories = page.categories.all()
        self.assertEqual(len(categories), 1)
        self.assertIn(new_category, categories)

    def test_full_update_recipe(self):
        """ Test updating a page with put for admin """
        page = sample_page()
        page.categories.add(sample_category())
        payload = {
            'title': 'Puslapis 1',
            'text': 'lipsum',
            'slug': 'puslapis-1'
        }
        url = detail_url(page.id)
        self.client.put(url, payload)

        page.refresh_from_db()
        self.assertEqual(page.title, payload['title'])
        self.assertEqual(page.text, payload['text'])
        self.assertEqual(page.slug, payload['slug'])
        categories = page.categories.all()
        self.assertEqual(len(categories), 0)

    def test_filter_pages_by_categories(self):
        """ Test returning pages with specific category for admin """
        page1 = sample_page(title='Page 1')
        page2 = sample_page(title='Page 2')
        category1 = sample_category(name='Puslapis')
        category2 = sample_category(name='Naujiena')
        page1.categories.add(category1)
        page2.categories.add(category2)
        page3 = sample_page(title='Page 3')

        res = self.client.get(
            ADMIN_PAGES_URL,
            {'categories': f'{category1.id},{category2.id}'}
        )

        serializer1 = PageSerializer(page1)
        serializer2 = PageSerializer(page2)
        serializer3 = PageSerializer(page3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)


class PageImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@gmail.com',
            'testpass'
        )
        self.user.is_staff = True
        self.client.force_authenticate(self.user)
        self.page = sample_page()

    def tearDown(self):
        self.page.image.delete()

    def test_upload_image_to_page(self):
        """ Test uploading an image to page """
        url = image_upload_url(self.page.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.page.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.page.image.path))

    def test_upload_image_bad_request(self):
        """ Test uploading an invalid image """
        url = image_upload_url(self.page.id)
        res = self.client.post(url, {'image': 'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
