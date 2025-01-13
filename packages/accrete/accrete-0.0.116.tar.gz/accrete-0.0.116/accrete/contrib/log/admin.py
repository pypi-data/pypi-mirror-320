import django.apps
from django.contrib import admin
from django import forms
from . import models

installed_models = django.apps.apps.get_models(
    include_auto_created=True, include_swapped=True
)
model_choices = [(
    f'{m._meta.app_label}.{m._meta.model_name}',
    f'{m._meta.app_label}.{m._meta.verbose_name}'
) for m in installed_models]


class LogConfigForm(forms.ModelForm):

    model = forms.ChoiceField(choices=model_choices)


class LogConfigFieldInLine(admin.TabularInline):

    model = models.LogConfigField


class LogConfigAdmin(admin.ModelAdmin):

    model = models.LogConfig
    list_display = ('model', 'ignore_errors')
    search_fields = ('pk', 'model')
    list_filter = ['ignore_errors']
    form = LogConfigForm
    inlines = [LogConfigFieldInLine]

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "model":
            kwargs["choices"] = [
                ("accepted", "Accepted"),
                ("denied", "Denied"),
            ]
        return super().formfield_for_choice_field(db_field, request, **kwargs)


admin.site.register(models.LogConfig, LogConfigAdmin)