import tempfile
import os
import random

from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Provider, ProviderService

from provider.serializers import ProviderSerializer, ProviderDetailSerializer


PROVIDERS_URL = reverse('provider:providers-list')


def image_upload_url(provider_id):
    # Return URL for provider image upload
    return reverse('provider:providers-upload-image', args=[provider_id])


def detail_url(provider_id):
    # Return provider detail URL
    return reverse('provider:providers-detail', args=[provider_id])


def sample_service(title, provider):
    # Create and return a sample service
    return ProviderService.objects.create(title=title, provider=provider)


def sample_provider_user(name):

    user = get_user_model().objects.create_user(
        name,
        'testpass'
    )
    user.is_company = True
    user.save()
    return user


def sample_provider(**params):
    # Create and return a sample provider
    rand = random.randint(1, 100)*5
    user = sample_provider_user('test2' + str(rand) + '@gmail.com')
    defaults = {
        'title': 'Sample provider',
        'description': 'Lorem ipsum',
        'admin_user': user
    }
    defaults.update(params)

    return Provider.objects.create(**defaults)


class PublicProviderApiTests(TestCase):
    """ Test unauthenticated provider API access """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        # Test that authentication ir required
        sample_provider()
        res = self.client.get(PROVIDERS_URL)

        providers = Provider.objects.all().order_by('-id')
        serializer = ProviderSerializer(providers, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_view_provider_detail(self):
        """ Test viewing a provider details """
        provider = sample_provider()

        url = detail_url(provider.id)
        res = self.client.get(url)

        serializer = ProviderDetailSerializer(provider)
        self.assertEqual(res.data, serializer.data)

    def test_filter_providers_by_services(self):
        """ Test returning providers with specific service """
        provider1 = sample_provider(title='Provider 1')
        provider2 = sample_provider(title='Provider 2')
        service1 = sample_service(title='Puslapis', provider=provider1)
        service2 = sample_service(title='Naujiena', provider=provider2)
        provider3 = sample_provider(title='Provider 3')

        res = self.client.get(
            PROVIDERS_URL,
            {'services': f'{service1.id},{service2.id}'}
        )

        serializer1 = ProviderSerializer(provider1)
        serializer2 = ProviderSerializer(provider2)
        serializer3 = ProviderSerializer(provider3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_partial_update_provider(self):
        """ Test updating a provider with patch """
        provider = sample_provider()
        new_service = sample_service(title='Service1', provider=provider)

        payload = {'title': 'Provider 1', 'services': [new_service.id]}
        url = detail_url(provider.id)
        self.client.patch(url, payload)

        provider.refresh_from_db()
        self.assertNotEqual(provider.title, payload['title'])


class PrivateProviderApiTests(TestCase):
    # Test unauthenticated provider API access

    def setUp(self):
        self.client = APIClient()
        self.z = get_user_model().objects.create_user(
            'test@gmail.com',
            'testpass'
        )
        self.z.is_staff = True
        self.client.force_authenticate(self.z)

    def test_retrieve_providers(self):
        """ Test retrieving a list of providers for admin """
        sample_provider(title='Provider 1')

        res = self.client.get(PROVIDERS_URL)

        providers = Provider.objects.all().order_by('-id')
        serializer = ProviderSerializer(providers, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(len(serializer.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_provider_detail(self):
        """ Test viewing a provider details for admin """
        provider = sample_provider()
        sample_service(title="Puslapių kūrimas", provider=provider)

        url = detail_url(provider.id)
        res = self.client.get(url)

        serializer = ProviderDetailSerializer(provider)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_provider(self):
        """ Test creating provider """
        payload = {
            'title': 'Puslapis 1',
            'description': 'Lorem ipsum',
            'admin_user': self.z.id
        }
        res = self.client.post(PROVIDERS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_filter_providers_by_services(self):
        """ Test returning providers with specific service for admin """
        provider1 = sample_provider(title='Provider 1')
        provider2 = sample_provider(title='Provider 2')
        service1 = sample_service(title='Puslapis', provider=provider1)
        service2 = sample_service(title='Naujiena', provider=provider2)
        provider3 = sample_provider(title='Provider 3')

        res = self.client.get(
            PROVIDERS_URL,
            {'services': f'{service1.id},{service2.id}'}
        )

        serializer1 = ProviderSerializer(provider1)
        serializer2 = ProviderSerializer(provider2)
        serializer3 = ProviderSerializer(provider3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)


class ProviderImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@gmail.com',
            'testpass'
        )
        self.user.is_staff = True
        self.client.force_authenticate(self.user)
        self.provider = sample_provider()

    def tearDown(self):
        self.provider.image.delete()

    def test_upload_image_to_provider(self):
        """ Test uploading an image to provider """
        url = image_upload_url(self.provider.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.provider.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.provider.image.path))

    def test_upload_image_bad_request(self):
        """ Test uploading an invalid image """
        url = image_upload_url(self.provider.id)
        res = self.client.post(url, {'image': 'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
