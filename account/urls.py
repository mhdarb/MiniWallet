from django.urls import path

from rest_framework.routers import DefaultRouter

from django.urls import path

from account.views.customer_view import AccountInitView, CustomerRegistrationView
from account.views.wallet_view import WalletViewSet
router = DefaultRouter()

router.register(
    r'wallet',
    WalletViewSet,
    basename = 'wallet'
)

urlpatterns = [
    path('init/', AccountInitView.as_view(), name='account-init'),
    path('register/', CustomerRegistrationView.as_view(), name='customer-registration'),
]

urlpatterns += router.urls