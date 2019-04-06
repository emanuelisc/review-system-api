from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ticket


TICKETS_URL = reverse('ticket:tickets-list')


def detail_url(ticket_id):
    # Return ticket detail URL
    return reverse('ticket:tickets-detail', args=[ticket_id])


def sample_ticket(**params):
    # Create and return a sample ticket
    defaults = {
        'title': 'Sample ticket',
        'description': 'Lorem ipsum'
    }
    defaults.update(params)

    return Ticket.objects.create(**defaults)


class PublicTicketApiTests(TestCase):
    """ Test unauthenticated ticket API access """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        # Test that authentication ir required
        sample_ticket()
        res = self.client.get(TICKETS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatePageApiTests(TestCase):
    # Test unauthenticated ticket API access

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_tickets(self):
        """ Test retrieving a list of tickets """
        sample_ticket(title='Neveikia sąrašas')

        res = self.client.get(TICKETS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_ticket(self):
        """ Test creating ticket """
        payload = {
            'title': 'Klaida Nr. 1',
            'description': 'Lorem ipsum'
        }
        res = self.client.post(TICKETS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        ticket = Ticket.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(ticket, key))
