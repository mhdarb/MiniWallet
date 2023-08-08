from django.contrib import admin
from django.apps import apps

# Register your models here.

app_config = apps.get_app_config('account')

for model in app_config.get_models():
    admin.site.register(model)