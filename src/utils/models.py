from django.db import models
from django.utils.translation import gettext_lazy as _


class Region(models.Model):
    name = models.CharField(_("name"), max_length=100)

    class Meta:
        verbose_name = _("Region")
        verbose_name_plural = _("Regions")

    def __str__(self):
        return self.name


class District(models.Model):
    name = models.CharField(_("name"), max_length=100)
    region = models.ForeignKey(verbose_name=_("region"), to=Region, on_delete=models.CASCADE, related_name="districts")

    class Meta:
        verbose_name = _("District")
        verbose_name_plural = _("Districts")

    def __str__(self):
        return self.name


class Neighborhood(models.Model):
    name = models.CharField(_("name"), max_length=100)
    district = models.ForeignKey(verbose_name=_("district"), to=District, on_delete=models.CASCADE, related_name="neighborhoods")
    user = models.OneToOneField(verbose_name=_("user"), to="users.user", on_delete=models.CASCADE, related_name="neighborhood", null=True)

    class Meta:
        verbose_name = _("Neighborhood")
        verbose_name_plural = _("Neighborhoods")

    def __str__(self):
        return f"{self.name} ({self.district.name})"


class Inspector(models.Model):
    full_name = models.CharField(_("full_name"), max_length=100)
    phone = models.CharField(_("phone"), max_length=13, null=True, blank=True)
    neighborhood = models.OneToOneField(verbose_name=_("neighborhood"), to=Neighborhood, on_delete=models.CASCADE, related_name="inspector")
    user = models.OneToOneField(verbose_name=_("user"), to="users.user", on_delete=models.CASCADE, related_name="inspector")

    class Meta:
        verbose_name = _("Inspector")
        verbose_name_plural = _("Inspectors")

    def __str__(self):
        return self.full_name


class SettingsKey(models.Model):
    name = models.CharField(_("name"), max_length=255)
    key = models.CharField(_("key"), max_length=100, unique=True)
    value = models.CharField(_("value"), max_length=255)

    class Meta:
        verbose_name = _("Settings key")
        verbose_name_plural = _("Settings keys")

    def __str__(self):
        return self.name


class DistrictMonitoring(District):
    class Meta:
        proxy = True
        verbose_name = _("Monitoring")
        verbose_name_plural = _("Monitoring")


def get_limits():
    defaults = {
        "last_psychiatric_appointment_days": 30,
        "last_home_visit_by_doctor_days": 30,
        "last_hospitalization_to_days": 180,
    }

    limits = {}

    for key, default_value in defaults.items():
        obj, created = SettingsKey.objects.get_or_create(
            key=key,
            defaults={"value": str(default_value)}
        )
        limits[key] = int(obj.value)
    return limits