
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.contrib.auth.models import User

from account.models import Account, Customer
from account.services import build_failure_response, build_success_response

    
class CustomerRegistrationView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if username is None or password is None:
            return Response({'error': 'Please provide both username and password.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=username).exists():
            error = "Username already exists."
            response_dict = build_failure_response(error)
            return Response(response_dict, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create_user(username=username, password=password)
        customer = Customer.objects.create(user=user)
        response_dict = build_success_response({'customer_xid': customer.xid})
        return Response(response_dict, status=status.HTTP_201_CREATED)
    
    
class AccountInitView(APIView):
    def post(self, request, *args, **kwargs):
        customer_xid = request.data.get('customer_xid')
        if not customer_xid:
            error_dict = {
                "customer_xid": [
                    "Missing data for required field."
                ]
            }
            response_dict = build_failure_response(error_dict)
            return Response(response_dict, status=status.HTTP_400_BAD_REQUEST)

        customer = Customer.objects.filter(xid=customer_xid).first()      
        if not customer:
            error_dict = {
                "customer_xid": [
                    "Please provide a valid customer xid"
                ]
            }
            response_dict = build_failure_response(error_dict)
            return Response(response_dict, status=status.HTTP_400_BAD_REQUEST)
        if not customer.account:
            account = Account.objects.create(owned_by=customer)
            customer.account = account
            customer.save()
        token, created = Token.objects.get_or_create(user=customer.user)
        response = build_success_response({'token': token.key})
        return Response(response, status=status.HTTP_200_OK)

