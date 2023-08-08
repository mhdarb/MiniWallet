from django.db import models
import uuid
from django.contrib.auth.models import User

WITHDRAW = 'withdraw'
DEPOSIT = 'deposit'

TRANSACTION_TYPE = (
    (WITHDRAW,'withdraw'),
    (DEPOSIT,'deposit'),
)

SUCCESS = 'success'
FAILED = 'failed'

TRANSACTION_STATUS = (
    (SUCCESS,'success'),
    (FAILED,'failed'),
)

DISABLED = 'disabled'
ENABLED = 'enabled'

ACCOUNT_STATUS = (
    (DISABLED,'disabled'),
    (ENABLED,'enabled'),
)

class Customer(models.Model):
    xid = models.UUIDField(default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account = models.OneToOneField('Account', on_delete=models.SET_NULL, null=True, blank=True, related_name='customer_relation')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Account(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owned_by = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='account_relation')
    status = models.CharField(choices=ACCOUNT_STATUS, default=DISABLED, max_length=50)
    balance = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, blank=False)
    type = models.CharField(choices=TRANSACTION_TYPE, max_length=50)
    status = models.CharField(choices=TRANSACTION_STATUS, max_length=50)
    reference_id = models.UUIDField(blank=False)
    amount = models.IntegerField()
    transacted_at = models.DateTimeField(auto_now_add=True)