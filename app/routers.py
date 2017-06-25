from django.conf import settings

from rest_framework.routers import DefaultRouter

from useraccounts.views import EmailViewSet
from useraccounts.views import UserViewSet
from useraccounts.views import JWTViewSet


router = DefaultRouter()


# === ADD CUSTOM ROUTERS BELOW THIS LINE ======================================

# === ADD CUSTOM ROUTERS ABOVE THIS LINE ======================================


if "useraccounts" in settings.INSTALLED_APPS:
    router.register(r"jwt", JWTViewSet, "jwt")
    router.register(r"email", EmailViewSet, "email")
    router.register(r"user", UserViewSet, "user")
