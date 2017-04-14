from django.conf import settings

from rest_framework.routers import DefaultRouter

from useraccounts.views import AccountViewSet
from useraccounts.views import EmailViewSet


router = DefaultRouter()


# === ADD CUSTOM ROUTERS BELOW THIS LINE ======================================

# === ADD CUSTOM ROUTERS ABOVE THIS LINE ======================================


if "useraccounts" in settings.INSTALLED_APPS:
    router.register(r"account", AccountViewSet, base_name="account")
    router.register(r"email", EmailViewSet, base_name="email")
