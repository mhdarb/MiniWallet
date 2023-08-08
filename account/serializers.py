from rest_framework import serializers
from .models import Transaction, TRANSACTION_TYPE, TRANSACTION_STATUS

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('id', 'account', 'type', 'status', 'reference_id', 'amount', 'transacted_at')

    # Optionally, you can define choices explicitly for type and status fields
    type = serializers.ChoiceField(choices=TRANSACTION_TYPE)
    status = serializers.ChoiceField(choices=TRANSACTION_STATUS)
