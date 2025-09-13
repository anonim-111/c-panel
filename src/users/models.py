from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    telegram_id = models.CharField(_("telegram ID"), max_length=20, null=True, blank=True)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")


class DistrictAdmin(models.Model):
    district = models.ForeignKey(verbose_name=_("district"), to="utils.District", on_delete=models.CASCADE, related_name="admins")
    user = models.OneToOneField(verbose_name=_("user"), to="users.user", on_delete=models.CASCADE, related_name="district")

    class Meta:
        verbose_name = _("District admin")
        verbose_name_plural = _("District admins")


class RegionAdmin(models.Model):
    region = models.ForeignKey(verbose_name=_("region"), to="utils.Region", on_delete=models.CASCADE, related_name="admins")
    user = models.OneToOneField(verbose_name=_("user"), to="users.user", on_delete=models.CASCADE, related_name="region")

    class Meta:
        verbose_name = _("Region admin")
        verbose_name_plural = _("Region admins")