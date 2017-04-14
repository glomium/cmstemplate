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

# from .models import User
from .permissions import EmailPermissions
from .serializers import EmailDetailSerializer
from .serializers import EmailListSerializer
from .serializers import EmailValidate
from .serializers import LoginSerializer
# from .serializers import PasswordValidate
# from .serializers import UsernameValidate
# from .serializers import UserSerializer
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


class AccountViewSet(viewsets.ViewSet):
    """
    """

    serializers = {
        'login': LoginSerializer,
        # 'validate_password': PasswordValidate,
        # 'validate_username': UsernameValidate,
    }

    def get_serializer(self, *args, **kwargs):
        return self.serializers.get(self.action)(*args, **kwargs)

    @method_decorator(sensitive_post_parameters())  # TODO: check if functional / needed
    @list_route(methods=["post"])
    def login(self, request, **kwargs):

        # Logout old user
        if self.request.user.is_authenticated():
            logout(request)

        user = authenticate(username=request.data['username'], password=request.data['password'], request=request)

        if user is None:
            return Response(
                {"detail": _("Invalid login - please enter correct login data")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        login(request, user)

        return Response(
            {"detail": _("Logged in")},
            status=status.HTTP_200_OK,
        )

    @list_route(methods=["get"])
    def logout(self, request, **kwargs):
        if self.request.user.is_authenticated():
            logout(request)
            return Response({"detail": _("Logged out")})
        else:
            return Response({"detail": _("Already logged out")}, status=status.HTTP_400_BAD_REQUEST)

#   @list_route(methods=['get', 'post'])
#   def validate_password(self, request, **kwargs):
#       if self.request.method == "GET":
#           return Response({"help_text": help_text_password()})
#       else:
#           serializer = self.get_serializer(instance=self.request.user, data=request.data)
#           serializer.is_valid(raise_exception=True)
#           return Response({"detail": _("Password is valid")})

#   @list_route(methods=['post'])
#   def validate_username(self, request, **kwargs):
#       # TODO change field to foreign-key adding validation for taken usernames
#       serializer = self.get_serializer(instance=self.request.user, data=request.data)
#       serializer.is_valid(raise_exception=True)
#       return Response({"detail": _("Username is valid")})


'''
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
'''


'''
class LoginView(FormView):
    default_redirect_to = settings.LOGIN_REDIRECT_URL
    form_class = AuthenticationForm
    redirect_field_name = REDIRECT_FIELD_NAME
    template_name = "useraccounts/login.html"

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        request.session.set_test_cookie()
        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(LoginView, self).get_form_kwargs()
        kwargs.update({"request": self.request})
        return kwargs

    def form_valid(self, form):
        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()

        # Okay, security check complete. Log the user in.
        login(self.request, form.get_user())
        return super(LoginView, self).form_valid(form)

    def get_success_url(self):
        redirect_to = self.request.POST.get(
            self.redirect_field_name,
            self.request.GET.get(self.redirect_field_name, '')
        )

        # Ensure the user-originating redirection url is safe.
        if not is_safe_url(url=redirect_to, host=self.request.get_host()):
            redirect_to = resolve_url(self.default_redirect_to)

        return redirect_to
'''


'''
class EmailMixin(object):

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(EmailMixin, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.emails.all()


class EmailEditMixin(EmailMixin):
    slug_field = 'email'
    slug_url_kwarg = 'email'

    def get_queryset(self):
        return super(EmailEditMixin, self).get_queryset().filter(is_primary=False)


class EmailListView(EmailMixin, ListView):
    pass


class EmailDeleteView(EmailEditMixin, DeleteView):
    template_name = "useraccounts/email_delete_view.html"
    success_url = appsettings.REDIRECT_EMAIL_DELETE

    def get_success_url(self):
        if self.success_url:
            return resolve_url(self.success_url)


class EmailCreateView(EmailEditMixin, CreateView):
    form_class = EmailCreateForm
    template_name = "useraccounts/email_create_view.html"
    success_url = appsettings.REDIRECT_EMAIL_CREATE

    def get_form_kwargs(self):
        kwargs = super(EmailCreateView, self).get_form_kwargs()
        kwargs.update({"request": self.request, "user": self.request.user})
        return kwargs

    def get_success_url(self):
        if self.success_url:
            return resolve_url(self.success_url)


class EmailUpdateView(SingleObjectMixin, TemplateView):
    template_name = "useraccounts/email_update_view.html"
    success_url = appsettings.REDIRECT_EMAIL_UPDATE
    slug_field = 'email'
    slug_url_kwarg = 'email'

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super(EmailUpdateView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.emails.filter(is_primary=False, is_valid=True)

    def get_success_url(self):
        return self.success_url

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_primary = True
        self.object.save()

        success_url = self.get_success_url()
        if success_url:
            next_page = resolve_url(success_url)
            if next_page:
                return HttpResponseRedirect(next_page)
        return super(EmailUpdateView, self).get(request, *args, **kwargs)


class EmailResendView(SingleObjectMixin, TemplateView):
    template_name = "useraccounts/email_resend_view.html"
    success_url = appsettings.REDIRECT_EMAIL_RESEND
    slug_field = 'email'
    slug_url_kwarg = 'email'

    @method_decorator(never_cache)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(EmailResendView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.emails.all().filter(is_valid=False)

    def get_success_url(self):
        if self.success_url:
            return resolve_url(self.success_url)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.send_validation(request=self.request, skip=False)
        success_url = self.get_success_url()
        if success_url:
            return HttpResponseRedirect(next_page)
        return super(EmailResendView, self).get(request, *args, **kwargs)


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
