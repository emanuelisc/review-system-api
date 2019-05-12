from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from user.serializers import AdminUsersSerializer


USERS_URL = reverse('user:user-list')


def detail_url(user_id):
    # Return user detail URL
    return reverse('user:user-detail', args=[user_id])


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicAdminApiTests(TestCase):
    # Test unauthenticated user API access

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        # Test that authentication ir required
        res = self.client.get(USERS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class UnAuthUserApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_users(self):
        # Test retrieving a list of users
        payload1 = {
            'email': 'test1@gmail.com',
            'password': 'testpass',
        }
        payload2 = {
            'email': 'test2@gmail.com',
            'password': 'testpass',
        }
        create_user(**payload1)
        create_user(**payload2)

        res = self.client.get(USERS_URL)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class PrivateUserApiTests(TestCase):
    # Test unauthentivated user API access

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'testpass'
        )
        self.user.is_staff = True
        self.client.force_authenticate(self.user)

    def test_retrieve_users(self):
        # Test retrieving a list of users
        payload1 = {
            'email': 'test1@gmail.com',
            'password': 'testpass',
        }
        payload2 = {
            'email': 'test2@gmail.com',
            'password': 'testpass',
        }
        create_user(**payload1)
        create_user(**payload2)

        res = self.client.get(USERS_URL)
        # print(res.data['results'])
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 3)

    def test_view_user_detail(self):
        # Test viewing a user detail
        payload = {
            'email': 'test1@gmail.com',
            'password': 'testpass',
        }
        user = create_user(**payload)

        url = detail_url(user.id)
        res = self.client.get(url)

        serializer = AdminUsersSerializer(user)
        self.assertEqual(res.data, serializer.data)

    def test_create_user(self):
        # Test creating user
        payload = {
            'email': 'test1@gmail.com',
            'password': 'testpass',
            'name': 'testas',
            'is_company': True
        }
        res = self.client.post(USERS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(user, key))
