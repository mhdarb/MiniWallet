import enum
from functools import wraps

from account.models import Account, Customer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User


class responseStatus(enum.Enum):
    SUCCESS = "success"
    FAIL = "fail"

def build_success_response(data:dict) -> dict:
    response_dict = {
        "data" : data,
        "status" : responseStatus.SUCCESS.value,
    }
    return response_dict

def build_failure_response(error) -> dict:
    response_dict = {
        "error" : error,
        "status" : responseStatus.FAIL.value
    }
    return response_dict

def wallet_decorator(view_func):
    @wraps(view_func)
    def _wrapped_view(self, request, *args, **kwargs):
        customer = Customer.objects.filter(user=request.user).first()
        if not customer:
            error = "No such customer"
            response_dict = build_failure_response(error)
            return Response(response_dict, status=status.HTTP_400_BAD_REQUEST)
        account = Account.objects.filter(owned_by=customer).first()
        if not account:
            error = "No account associated with customer"
            response_dict = build_failure_response(error)
            return Response(response_dict, status=status.HTTP_400_BAD_REQUEST)
        self.account = account
        
        return view_func(self, request, *args, **kwargs)
    
    return _wrapped_view

