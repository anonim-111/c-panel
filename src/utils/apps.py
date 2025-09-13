from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import gettext_lazy as _


class UtilsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'utils'
    verbose_name = _("Utils")

    def ready(self):
        from .signals import create_virtual_permissions
        post_migrate.connect(create_virtual_permissions, sender=self)