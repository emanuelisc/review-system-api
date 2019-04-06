from rest_framework import serializers

from core.models import Ticket


class TicketSerializer(serializers.ModelSerializer):
    # Serialize a ticket

    class Meta:
        model = Ticket
        fields = (
            'id',
            'title',
            'description',
            'date',
            'object_type',
            'object_id',
            'is_active',
            'user'
        )
        read_only_fields = ('id',)
