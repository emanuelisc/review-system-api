from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from core.models import Ticket
from ticket import serializers


class TicketAdminViewSet(viewsets.ModelViewSet):
    # Manage ticket in the database
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, IsAdminUser, )
    serializer_class = serializers.TicketSerializer
    queryset = Ticket.objects.all()


class TicketViewSet(viewsets.ModelViewSet):
    # Manage ticket in the database
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.TicketSerializer
    queryset = Ticket.objects.all()

    def get_queryset(self):
        # Retrieve tickets
        queryset = self.queryset
        return queryset.filter(
            user=self.request.user
        ).order_by('-id').distinct()

    def get_serializer_class(self):
        # Return appropriate serializer class
        return self.serializer_class

    def perform_create(self, serializer):
        # Create a new serializer
        serializer.save(user=self.request.user)
