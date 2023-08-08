
import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework import status

from account.models import DEPOSIT, DISABLED, ENABLED, FAILED, SUCCESS, WITHDRAW, Transaction
from account.serializers import TransactionSerializer
from account.services import build_failure_response, build_success_response, wallet_decorator

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet

import threading
from django.db.models import F
import random
import time


class WalletViewSet(ViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @wallet_decorator
    def list(self, request):
        account = self.account
        if account.status == DISABLED:
            error = "Wallet disabled"
            response_dict = build_failure_response(error)
            return Response(response_dict, status=status.HTTP_400_BAD_REQUEST)
        response_data = {
            "wallet": {
                "id": account.id,
                "owned_by": account.owned_by.xid,
                "status": account.status,
                "enabled_at": account.updated_at,
                "balance": account.balance
            }
        }
        response_dict = build_success_response(response_data)
        return Response(response_dict, status=status.HTTP_200_OK)

    @wallet_decorator
    def create(self, request, *args, **kwargs):
        account = self.account
        if not account:
            error = "No account associated with customer"
            response_dict = build_failure_response(error)
            return Response(response_dict, status=status.HTTP_400_BAD_REQUEST)
        if account.status == ENABLED:
            error = "Already enabled"
            response_dict = build_failure_response(error)
            return Response(response_dict, status=status.HTTP_400_BAD_REQUEST)
        
        account.status = ENABLED
        account.save()

        response_data = {
            "wallet": {
                "id": account.id,
                "owned_by": account.owned_by.xid,
                "status": account.status,
                "enabled_at": account.updated_at,
                "balance": account.balance
            }
        }
        response_dict = build_success_response(response_data)
        return Response(response_dict, status=status.HTTP_201_CREATED)
    
    @wallet_decorator
    @action(methods=['get'], detail=False)    
    def transactions(self, request, *args, **kwargs):
        account = self.account
        if account.status == DISABLED:
            error = "Wallet disabled"
            response_dict = build_failure_response(error)
            return Response(response_dict, status=status.HTTP_400_BAD_REQUEST)
        
        transactions = Transaction.objects.filter(account=account).all()
        serializer = TransactionSerializer(transactions, many=True)

        response_dict = build_success_response({"transactions": serializer.data})
        return Response(response_dict, status=status.HTTP_201_CREATED)
    
    @wallet_decorator
    @action(methods=['post'], detail=False)    
    def deposits(self, request, *args, **kwargs):
        reference_id = request.data.get('reference_id')
        amount = int(request.data.get('amount'))
        if not reference_id or not amount:
            error_dict = {
                "customer_xid": [
                    "Missing data for required field."
                ]
            }
            response_dict = build_failure_response(error_dict)
            return Response(response_dict, status=status.HTTP_400_BAD_REQUEST)
        if amount<=0:
            error = "Deposit Amount must be greater than 0"
            response_dict = build_failure_response(error)
            return Response(response_dict, status=status.HTTP_400_BAD_REQUEST)
        
        account=self.account
        if account.status == DISABLED:
            error = "Wallet disabled"
            response_dict = build_failure_response(error)
            return Response(response_dict, status=status.HTTP_400_BAD_REQUEST)
        
        reference_id_exists = Transaction.objects.filter(reference_id=reference_id).exists()
        if not reference_id_exists:
            # Handling concurrency control with locking to maintain db consistency and integrity
            account_lock = threading.Lock()
            with account_lock:
                # generating time lag of around 5s for deposit delay
                sleep_time = random.uniform(1, 5)
                logging.info(f'Transaction deposit delay with {sleep_time}')
                time.sleep(sleep_time)
                account.balance = F('balance') + amount
                account.save()
            
            transaction = Transaction.objects.create(
                account = account,
                type = DEPOSIT,
                status = SUCCESS,
                reference_id = reference_id,
                amount = amount
            )
        else:
            transaction = Transaction.objects.create(
                account = account,
                type = DEPOSIT,
                status = FAILED,
                reference_id = reference_id,
                amount = amount
            )
        
        response_data = {
            "deposit": {
                "id": transaction.id,
                "deposited_by": account.owned_by.xid,
                "status": transaction.status,
                "deposited_at": transaction.transacted_at,
                "amount" : transaction.amount,
                "reference_id" : transaction.reference_id
            }
        }
        if transaction.status==SUCCESS:
            response_dict = build_success_response(response_data)
        else:
            response_dict = build_failure_response(response_data)
        return Response(response_dict, status=status.HTTP_201_CREATED)
    
    @wallet_decorator
    @action(methods=['post'], detail=False)    
    def withdrawals(self, request, *args, **kwargs):
        reference_id = request.data.get('reference_id')
        amount = int(request.data.get('amount'))
        if not reference_id or not amount:
            error_dict = {
                "customer_xid": [
                    "Missing data for required field."
                ]
            }
            response_dict = build_failure_response(error_dict)
            return Response(response_dict, status=status.HTTP_400_BAD_REQUEST)
        
        account = self.account
        if account.status == DISABLED:
            error = "Wallet disabled"
            response_dict = build_failure_response(error)
            return Response(response_dict, status=status.HTTP_400_BAD_REQUEST)
        if amount>account.balance:
            error = "Withdrawal amount must be less than current account balance"
            response_dict = build_failure_response(error)
            return Response(response_dict, status=status.HTTP_400_BAD_REQUEST)
        reference_id_exists = Transaction.objects.filter(reference_id=reference_id).exists()
        if not reference_id_exists:
            # Handling concurrency control with locking to maintain db consistency and integrity
            account_lock = threading.Lock()
            with account_lock:
                # generating time lag of around 5s for withdrawal delay
                sleep_time = random.uniform(1, 5)
                logging.info(f'Transaction withdrawal delay with {sleep_time}')
                time.sleep(sleep_time)
                account.balance = F('balance') - amount
                account.save()
            
            transaction = Transaction.objects.create(
                account = account,
                type = WITHDRAW,
                status = SUCCESS,
                reference_id = reference_id,
                amount = amount
            )
        else:
            transaction = Transaction.objects.create(
                account = account,
                type = WITHDRAW,
                status = FAILED,
                reference_id = reference_id,
                amount = amount
            )
        
        response_data = {
            "withdrawal": {
                "id": transaction.id,
                "withdrawn_by": account.owned_by.xid,
                "status": transaction.status,
                "withdrawn_at": transaction.transacted_at,
                "amount" : transaction.amount,
                "reference_id" : transaction.reference_id
            }
        }
        if transaction.status==SUCCESS:
            response_dict = build_success_response(response_data)
        else:
            response_dict = build_failure_response(response_data)
        return Response(response_dict, status=status.HTTP_201_CREATED)
    
    @wallet_decorator
    @action(methods=['patch'], detail=False)    
    def disabled(self, request, pk=None):
        is_disabled = request.data.get('is_disabled')
        account=self.account
        if account.status == DISABLED:
            error = "Wallet already disabled"
            response_dict = build_failure_response(error)
            return Response(response_dict, status=status.HTTP_400_BAD_REQUEST)

        account.status=DISABLED
        account.save()
        response_data = {
            "wallet": {
                "id": account.id,
                "owned_by": account.owned_by.xid,
                "status": account.status,
                "disabled_at": account.updated_at,
                "balance": account.balance
            }
        }
        response_dict = build_success_response(response_data)
        return Response(response_dict, status=status.HTTP_201_CREATED)