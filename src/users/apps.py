from django.apps import AppConfig, apps
from django.utils.translation import gettext_lazy as _



class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = _("Users")

    def ready(self):
        from django.contrib.auth.models import Group
        Group._meta.verbose_name = _("Group")
        Group._meta.verbose_name_plural = _("Groups")
