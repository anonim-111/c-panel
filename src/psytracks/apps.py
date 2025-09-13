from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class PsytracksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'psytracks'
    verbose_name = _("Psytracks")
