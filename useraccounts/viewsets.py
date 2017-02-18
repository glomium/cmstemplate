#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.decorators import list_route
from rest_framework.response import Response

from .models import Email
from .models import User
from .permissions import EmailPermissions
from .serializers import EmailDetailSerializer
from .serializers import EmailListSerializer
from .serializers import EmailValidate
from .serializers import PasswordValidate
from .serializers import UsernameValidate
from .serializers import UserSerializer
from .validators import help_text_password


class EmailViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = Email.objects.all()
    serializer_class = EmailListSerializer
    permission_classes = [EmailPermissions]
    lookup_value_regex = '[\w.@+-]+' 
    lookup_field = "email"
    lookup_url_kwarg = "email"

    serializers = {
        'retrieve': EmailDetailSerializer,
        'update': EmailDetailSerializer,
        'update_partial': EmailDetailSerializer,
        'validate': EmailValidate,
    }

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.serializer_class)

    def get_queryset(self):
        return self.request.user.emails.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        serializer.instance.send_validation(self.request)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    @detail_route(methods=['post'])
    def validate(self, request, pk=None, **kwargs):
        instance = self.get_object()

        if not instance.is_valid:
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return Response({"detail": _("Email is valid")})

    @detail_route(methods=['get'])
    def resend_validation(self, request, pk=None, **kwargs):
        instance = self.get_object()

        if instance.is_valid:
            return Response({"detail": _("Email is valid")})
        else:
            instance.send_validation(request=self.request)
            return Response({"detail": _("Validation information send")})


class AccountViewSet(viewsets.ViewSet):
    """
    """

    serializers = {
        'validate_password': PasswordValidate,
        'validate_username': UsernameValidate,
    }

    def get_serializer(self, *args, **kwargs):
        return self.serializers.get(self.action)(*args, **kwargs)

    @list_route(methods=['get', 'post'])
    def validate_password(self, request, **kwargs):
        if self.request.method == "GET":
            return Response({"help_text": help_text_password()})
        else:
            serializer = self.get_serializer(instance=self.request.user, data=request.data)
            serializer.is_valid(raise_exception=True)
            return Response({"detail": _("Password is valid")})

    @list_route(methods=['post'])
    def validate_username(self, request, **kwargs):
        # TODO change field to foreign-key adding validation for taken usernames
        serializer = self.get_serializer(instance=self.request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"detail": _("Username is valid")})

#   @list_route()
#   def login(self, request, **kwargs):
#       return Response()

#   @list_route()
#   def logout(self, request, **kwargs):
#       return Response()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_value_regex = '[\w.@+-]+' 
    lookup_field = "username"
    lookup_url_kwarg = "username"

    @detail_route()
    def groups(self, request, **kwargs):
        user = self.get_object()
        groups = user.groups.all()
        return Response([group.name for group in groups])
