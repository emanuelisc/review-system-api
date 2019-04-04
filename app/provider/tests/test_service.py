from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Provider, ProviderService

from provider.serializers import ProviderServiceSerializer


SERVICES_URL = reverse('provider:adminservice-list')
SERVICESLIST_URL = reverse('provider:services-list')


def sample_service(title='Maisto gaminimas', description='Lorem ipsum'):
    # Create and return a sample service
    provider = sample_provider()
    return ProviderService.objects.create(title=title, description=description, provider=provider)


def sample_provider(title='Maistininkas ir Ko', description='Lorem ipsum'):
    # Create and return a sample provider
    return Provider.objects.create(title=title, description=description)


def detail_url(service_id):
    # Return service detail URL
    return reverse('provider:adminservice-detail', args=[service_id])


def detail_public_url(service_id):
    # Return service detail URL
    return reverse('provider:services-detail', args=[service_id])


class PublicServiceApiTests(TestCase):
    # Test the publicly available services API

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_service_list(self):
        # Test retrieving a list of services
        provider = sample_provider()
        ProviderService.objects.create(
            title='Maisto gaminimas',
            description='Lorem ipsum',
            provider=provider
        )
        ProviderService.objects.create(
            title='Maisto gaminimas',
            description='Langų valymas',
            provider=provider
        )

        res = self.client.get(SERVICESLIST_URL)

        services = ProviderService.objects.all().order_by('-title')
        serializer = ProviderServiceSerializer(services, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_service_public_unsuccessfull(self):
        """ Test create a new service for unauthorized on public end """
        payload = {'title': 'Naujiena'}
        res = self.client.post(SERVICESLIST_URL, payload)

        exists = ProviderService.objects.filter(
            title=payload['title'],
        ).exists()
        self.assertFalse(exists)
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_service_unsuccessfull(self):
        """ Test create a new service for unauthorized """
        payload = {'title': 'Naujiena'}
        res = self.client.post(SERVICES_URL, payload)

        exists = ProviderService.objects.filter(
            title=payload['title'],
        ).exists()
        self.assertFalse(exists)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_service_details(self):
        """ Test service details public """
        payload = {'title': 'Maisto gaminimas'}
        service = sample_service()
        exists = ProviderService.objects.filter(
            title=payload['title'],).exists()
        self.assertTrue(exists)

        url = detail_public_url(service.id)
        res = self.client.get(url)
        serializer = ProviderServiceSerializer(service)

        self.assertEqual(res.data, serializer.data)

    def test_service_delete(self):
        """ Test service delete public """
        payload = {'title': 'Maisto gaminimas'}
        service = sample_service()
        exists = ProviderService.objects.filter(
            title=payload['title'],).exists()
        self.assertTrue(exists)

        url = detail_url(service.id)
        res = self.client.get(url)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAdminServiceApiTests(TestCase):
    # Test the private services API

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'testpass'
        )
        self.user.is_staff = True
        self.client.force_authenticate(self.user)

    def test_create_service_successfull(self):
        """ Test create a new service """
        provider = sample_provider()
        payload = {
            'title': 'Maisto ruosimas2',
            'description': 'Lorem ipsum2',
            'provider': provider.id
        }
        res1 = self.client.post(SERVICES_URL, payload)
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        res = self.client.get(SERVICES_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # self.assertTrue(exists)
        self.assertEqual(len(res.data), 1)

    def test_service_details(self):
        """ Test service details """
        provider = sample_provider()
        payload = {
            'title': 'Maisto ruošimas',
            'description': 'Lorem ipsum',
            'provider': provider
        }
        service = sample_service(title='Maisto ruošimas')
        exists = ProviderService.objects.filter(
            title=payload['title'],).exists()
        self.assertTrue(exists)

        url = detail_url(service.id)
        res = self.client.get(url)
        serializer = ProviderServiceSerializer(service)

        self.assertEqual(res.data, serializer.data)

    def test_service_delete(self):
        """ Test service delete """
        payload = {'title': 'Maisto gaminimas'}
        service = sample_service()
        exists = ProviderService.objects.filter(
            title=payload['title'],).exists()
        self.assertTrue(exists)

        url = detail_url(service.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_service_invalid(self):
        # Test creating invalid service fails
        payload = {'title': ''}
        res = self.client.post(SERVICES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_services_assigned_to_providers(self):
        # Test filtering services by those assigned to providers
        provider1 = Provider.objects.create(
            title='Maistas ir Ko',
            description='Lorem ipsum'
        )
        provider2 = Provider.objects.create(
            title='Langdita',
            description='Lorem ipsum'
        )
        service1 = ProviderService.objects.create(
            title='Maisto gaminimas',
            description='Lorem ipsum',
            provider=provider1
        )
        service2 = ProviderService.objects.create(
            title='Langu valymas',
            description='Lorem ipsum',
            provider=provider1
        )

        res = self.client.get(SERVICES_URL, {'assigned_only': 1})

        serializer1 = ProviderServiceSerializer(service1)
        serializer2 = ProviderServiceSerializer(service2)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
