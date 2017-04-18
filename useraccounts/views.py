#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

# from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
# from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
# from django.http import HttpResponseRedirect
from django.http import Http404
# from django.shortcuts import redirect
from django.shortcuts import resolve_url
from django.utils.decorators import method_decorator
# from django.utils.http import is_safe_url
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
# from django.views.generic.base import TemplateView
# from django.views.generic.list import ListView
# from django.views.generic.detail import DetailView
from django.views.generic.detail import SingleObjectMixin
# from django.views.generic.edit import CreateView
# from django.views.generic.edit import DeleteView
from django.views.generic.edit import FormView
# from django.views.generic.edit import UpdateView

from .conf import settings as appsettings
# from .forms import AuthenticationForm
from .forms import PasswordChangeForm
from .forms import PasswordSetForm
from .forms import PasswordRecoverForm
# from .forms import EmailCreateForm
from .models import Email

from django.utils.translation import ugettext_lazy as _

from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import detail_route
from rest_framework.decorators import list_route
from rest_framework.response import Response

from .models import User
from .permissions import EmailPermissions
from .serializers import EmailDetailSerializer
from .serializers import EmailListSerializer
from .serializers import EmailValidate
from .serializers import LoginSerializer
# from .serializers import PasswordValidate
# from .serializers import UsernameValidate
from .serializers import UserSerializer
# from .validators import help_text_password


class EmailViewSet(viewsets.ModelViewSet):
    """
    """

    # queryset = Email.objects.all()
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
        else:
            return Response({"detail": _("Email is valid")}, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['get'])
    def resend(self, request, pk=None, **kwargs):
        instance = self.get_object()

        if instance.is_valid:
            return Response({"detail": _("Email is valid")}, status=status.HTTP_400_BAD_REQUEST)
        else:
            instance.send_validation(request=self.request)
            return Response({"detail": _("Validation information send")})


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_value_regex = '[\w.@+-]+'
    lookup_field = "username"
    lookup_url_kwarg = "username"

    serializers = {
        'login': LoginSerializer,
    }

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.serializer_class)

    @list_route(methods=["post"])
    def login(self, request, **kwargs):

        # Logout old user
        if self.request.user.is_authenticated():
            logout(request)

        user = authenticate(
            username=request.data['credentials'],
            password=request.data['password'],
            request=request
        )

        if user is None:
            return Response(
                {
                    "message": _("Invalid login - please enter correct login data"),
                    "user": {
                        "id": None,
                        "name": None,
                        "full_name": None,
                        "email": None,
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        login(request, user)

        return Response(
            {
                "message": _("Logged in"),
                "user": {
                    "id": user.pk,
                    "name": user.username,
                    "full_name": user.get_full_name(),
                    "email": user.email,
                },
            },
            status=status.HTTP_200_OK,
        )

    @list_route(methods=["get"])
    def logout(self, request, **kwargs):
        if self.request.user.is_authenticated:
            logout(request)
            return Response(
                {
                    "message": _("Logged out"),
                    "user": {
                        "id": None,
                        "name": None,
                        "full_name": None,
                        "email": None,
                    },
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "message": _("Logged out"),
                    "user": {
                        "id": None,
                        "name": None,
                        "full_name": None,
                        "email": None,
                    },
                },
                status=status.HTTP_200_OK,
            )

    @list_route(methods=["get"])
    def account(self, request, **kwargs):
        if self.request.user.is_authenticated:
            return Response(
                {
                    "message": _("Logged in"),
                    "user": {
                        "id": user.pk,
                        "name": user.username,
                        "full_name": user.get_full_name(),
                        "email": user.email,
                    },
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "message": _("Logged out"),
                    "user": {
                        "id": None,
                        "name": None,
                        "full_name": None,
                        "email": None,
                    },
                },
                status=status.HTTP_200_OK,
            )

    @detail_route(methods=["get"])
    def groups(self, request, **kwargs):
        user = self.get_object()
        groups = user.groups.all()
        return Response([group.name for group in groups])

    '''
    from __future__ import unicode_literals

    from django.contrib.auth import authenticate
    from django.utils.translation import ugettext as _

    from .authentication import JWTAuthentication
    from .utils import payload_handler
    from .utils import encode_handler
    from .utils import payload_update

    from rest_framework.exceptions import AuthenticationFailed
    from rest_framework.response import Response
    from rest_framework.status import HTTP_400_BAD_REQUEST
    from rest_framework.status import HTTP_401_UNAUTHORIZED
    from rest_framework.views import APIView

    permission_classes = ()
    authentication_classes = ()

    @list_route(methods=["get"])
    def jwt_verify(self, request, **kwargs):
        try:
            auth = JWTAuthentication().authenticate(request)
        except AuthenticationFailed:
            return Response({'token': None}, status=HTTP_401_UNAUTHORIZED)
        if not auth:
            return Response({'token': None}, status=HTTP_401_UNAUTHORIZED)
        return Response({'token': auth[1]})

    @list_route(methods=["post"])
    def jwt_generate(self, request, **kwargs):
        credentials = dict(request.data.items())
        credentials['request'] = request
        user = authenticate(**credentials)

        if user:
            if not user.is_active:
                msg = _('User account is disabled.')
                return Response({'error': msg}, status=HTTP_401_UNAUTHORIZED)
            return Response({'token': encode_handler(payload_handler(user))})

        msg = _('Unable to login with provided credentials.')
        return Response({'error': msg}, status=HTTP_400_BAD_REQUEST)

    @list_route(methods=["put"])
    def jwt_refresh(self, request, **kwargs):
        try:
            auth = JWTAuthentication().authenticate(request, payload=True)
        except AuthenticationFailed:
            return Response({'token': None}, status=HTTP_401_UNAUTHORIZED)
        if not auth:
            return Response({'token': None}, status=HTTP_401_UNAUTHORIZED)

        if not auth[0].is_active:
            msg = _('User account is disabled.')
            return Response({'error': msg}, status=HTTP_401_UNAUTHORIZED)

        return Response({'token': encode_handler(payload_update(auth[1]))})
    '''

    '''
    @list_route(methods=["post"])
    def password_recover(self, request, **kwargs):
        pass

    @list_route(methods=["post"])
    def password_change(self, request, **kwargs):
        pass

    @list_route(methods=["post"])
    def password_set(self, request, **kwargs):
        pass
    '''

'''
class PasswordRecoverView(FormView):
    """
    """
    template_name = "useraccounts/password_recover_form.html"
    success_url = appsettings.REDIRECT_RESTORE_CREATE
    form_class = PasswordRecoverForm

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        return super(PasswordRecoverView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(PasswordRecoverView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        form.save(commit=True)
        return super(PasswordRecoverView, self).form_valid(form)

    def get_success_url(self):
        if self.success_url:
            return resolve_url(self.success_url)
        return self.request.path


class PasswordChangeView(FormView):
    """
    """
    form_class = PasswordChangeForm
    success_url = appsettings.REDIRECT_CHANGE_SUCCESS
    template_name = "useraccounts/password_change_form.html"

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(PasswordChangeView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(PasswordChangeView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save(commit=True)
        return super(PasswordChangeView, self).form_valid(form)

    def get_success_url(self):
        if self.success_url:
            return resolve_url(self.success_url)
        return self.request.path


class PasswordSetView(SingleObjectMixin, FormView):
    template_name = "useraccounts/password_set_form.html"
    success_url = appsettings.REDIRECT_RESTORE_SUCCESS
    form_class = PasswordSetForm
    slug_field = 'email'
    slug_url_kwarg = 'email'

    # self.user_cache = authenticate(username=username, password=password, request=self.request)

    @method_decorator(never_cache)
    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):

        self.object = self.get_object()
        if not self.object.check_restore(self.kwargs.get('stamp', None), self.kwargs.get('crypt', None)):
            raise Http404

        return super(PasswordSetView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Email.objects.select_related('user').filter(is_valid=True)

    def get_form_kwargs(self):
        kwargs = super(PasswordSetView, self).get_form_kwargs()
        kwargs['user'] = self.object.user
        return kwargs

    def form_valid(self, form):
        form.save(commit=True)
        if appsettings.RESTORE_AUTOLOGIN \
                and (appsettings.LOGIN_EMAIL or appsettings.LOGIN_USERNAME) \
                and not self.request.user.is_authenticated():
            if appsettings.LOGIN_EMAIL:
                username = self.object.email
            else:
                username = self.object.user.username
            user = authenticate(
                username=username,
                password=form.cleaned_data.get('new_password1', None),
                request=self.request
            )
            login(self.request, user)
        return super(PasswordSetView, self).form_valid(form)

    def get_success_url(self):
        return resolve_url(self.success_url)
'''

'''
class EmailMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(EmailMixin, self).dispatch(request, *args, **kwargs)
    def get_queryset(self):
        return self.request.user.emails.all()


class EmailValidationView(SingleObjectMixin, TemplateView):
    template_name = "useraccounts/email_validation_view.html"
    success_url = appsettings.REDIRECT_EMAIL_VALIDATE
    slug_field = 'email'
    slug_url_kwarg = 'email'

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super(EmailValidationView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Email.objects.filter(is_valid=False)

    def get_success_url(self):
        if self.success_url:
            return resolve_url(self.success_url)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.check_validation(self.kwargs.get('stamp', None), self.kwargs.get('crypt', None)):
            raise Http404

        self.object.validate()

        success_url = self.get_success_url()
        if success_url:
            return HttpResponseRedirect(success_url)
        return super(EmailResendView, self).get(request, *args, **kwargs)
'''
