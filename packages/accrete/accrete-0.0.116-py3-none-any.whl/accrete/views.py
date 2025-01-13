import os
from functools import wraps
from django.http import HttpResponse, HttpResponseNotFound
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import login_required
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, get_object_or_404
from django.conf import settings
from accrete.models import Tenant, Member
from accrete.tenant import get_tenant
from . import config


class TenantRequiredMixin(LoginRequiredMixin):

    TENANT_NOT_SET_URL = None

    def dispatch(self, request, *args, **kwargs):
        res = super().dispatch(request, *args, **kwargs)
        tenant = self.get_tenant()
        if not tenant:
            return self.handle_tenant_not_set()
        return res

    def handle_tenant_not_set(self):
        return redirect(self.get_tenant_not_set_url())

    def get_tenant_not_set_url(self):
        tenant_not_set_url = (
                self.TENANT_NOT_SET_URL
                or settings.ACCRETE_TENANT_NOT_SET_URL
        )
        if not tenant_not_set_url:
            cls_name = self.__class__.__name__
            raise ImproperlyConfigured(
                f"{cls_name} is missing the tenant_not_set_url attribute. "
                f"Define {cls_name}.TENANT_NOT_SET_URL, "
                f"settings.ACCRETE_TENANT_NOT_SET_URL, or override "
                f"{cls_name}.get_tenant_not_set_url()."
            )
        return tenant_not_set_url

    @staticmethod
    def get_tenant():
        return get_tenant()


def tenant_required(
        redirect_field_name: str = None,
        login_url: str = None
):
    def decorator(f):
        @wraps(f)
        @login_required(
            redirect_field_name=redirect_field_name,
            login_url=login_url
        )
        def _wrapped_view(request, *args, **kwargs):
            tenant = request.tenant
            if not tenant:
                return redirect(config.ACCRETE_TENANT_NOT_SET_URL)
            return f(request, *args, **kwargs)
        return _wrapped_view
    return decorator


@tenant_required()
def get_tenant_file(request, tenant_id, filepath):
    tenant = get_object_or_404(Tenant, pk=tenant_id)
    if not request.user.is_staff:
        member = Member.objects.filter(user=request.user, tenant=tenant)
        if not member.exists():
            return HttpResponseNotFound()
    filepath = f'{settings.MEDIA_ROOT}/{tenant_id}/{filepath}'
    if not os.path.exists(filepath):
        return HttpResponseNotFound()
    with open(filepath, 'rb') as f:
        return HttpResponse(f)
