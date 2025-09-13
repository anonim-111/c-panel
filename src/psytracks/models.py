import os
import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class ReceivingSupportiveTherapyChoices(models.TextChoices):
    REGULARLY_RECEIVING = ("regularly_receiving", _("Regularly receiving"))
    NOT_RECEIVING = ("not_receiving", _("Not receiving"))
    QUICKLY_RECEIVING = ("quickly_receiving", _("Quickly receiving"))
    RERALY_RECEIVING = ("reraly_receiving", _("Reraly receiving"))


class AlcoholAndDrugUse(models.TextChoices):
    ALCOHOL_AND_DRUG = ("alcohol_and_drug", _("Alcohol and drug"))
    AlCOHOL = ("alcohol", _("Alcohol"))
    DRUG = ("drug", _("Drug"))
    NOT_CONSUME = ("not_consume", _("Not consume"))


class WhereIsNow(models.TextChoices):
    AT_HOME = ("at_home", _("At home"))
    IN_HOSPITAL = ("in_hospital", _("In hospital"))
    OUT_OF_THE_AREA = ("out_of_the_area", _("Out of the area"))
    ADDRESS_UNKNOWN = ("address_unknown", _("Address unknown"))


class Doctor(models.Model):
    full_name = models.CharField(_("full_name"), max_length=100)
    phone = models.CharField(_("phone"), max_length=13, null=True, blank=True)
    brigade_number = models.CharField(_("brigade_number"), max_length=50, null=True, blank=True)
    polyclinic_name = models.CharField(_("polyclinic name"), max_length=100, null=True, blank=True)
    birth_date = models.DateField(_("birth date"), null=True, blank=True)
    neighborhood = models.ForeignKey(verbose_name=_("neighborhood"), to="utils.Neighborhood", on_delete=models.CASCADE, related_name="doctors")

    class Meta:
        verbose_name = _("Doctor")
        verbose_name_plural = _("Doctors")

    def __str__(self):
        return self.full_name


class Psychiatrist(models.Model):
    full_name = models.CharField(_("full_name"), max_length=100)
    phone = models.CharField(_("phone"), max_length=13, null=True, blank=True)
    user = models.OneToOneField(verbose_name=_("user"), to="users.User", on_delete=models.CASCADE, related_name="psychiatrist")
    district = models.ForeignKey(verbose_name=_("district"), to="utils.District", on_delete=models.CASCADE, related_name="psychiatrists")

    class Meta:
        verbose_name = _("Psychiatrist")
        verbose_name_plural = _("Psychiatrists")

    def __str__(self):
        return self.full_name


class ReasonForSpecialConsideration(models.Model):
    name = models.CharField(_("name"), max_length=255)

    class Meta:
        verbose_name = _("Reason for special consideration")
        verbose_name_plural = _("Reasons for special consideration")

    def __str__(self):
        return self.name


class SocialDomesticEnvironment(models.Model):
    name = models.CharField(_("name"), max_length=255)

    class Meta:
        verbose_name = _("Social-domestic environment")
        verbose_name_plural = _("Social-domestic environments")

    def __str__(self):
        return self.name

def upload_to_psychiatric_appointment_file(instance, filename):
    today = datetime.date.today().strftime("%Y%m%d")
    obj_id = instance.pk or "new"
    return os.path.join("uploads", "psychiatric_appointment_file", str(obj_id), today, filename)

def upload_to_home_visit_by_doctor(instance, filename):
    today = datetime.date.today().strftime("%Y%m%d")
    obj_id = instance.pk or "new"
    return os.path.join("uploads", "home_visit_by_doctor", str(obj_id), today, filename)

def upload_to_last_hospitalization_from(instance, filename):
    today = datetime.date.today().strftime("%Y%m%d")
    obj_id = instance.pk or "new"
    return os.path.join("uploads", "last_hospitalization_from", str(obj_id), today, filename)

def upload_to_last_hospitalization_to(instance, filename):
    today = datetime.date.today().strftime("%Y%m%d")
    obj_id = instance.pk or "new"
    return os.path.join("uploads", "last_hospitalization_to", str(obj_id), today, filename)


def validate_file_size(value):
    max_size_mb = 20
    if value.size > max_size_mb * 1024 * 1024:
        raise ValidationError(
            _("The file size must not exceed %(size)d MB."),
            params={"size": max_size_mb},
        )

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    allowed_extensions = [".pdf", ".jpg"]

    if ext not in allowed_extensions:
        raise ValidationError(
            _("Only %(extensions)s files are allowed."),
            params={"extensions": ", ".join(allowed_extensions)},
        )

file_validators = [validate_file_size, validate_file_extension]


class Patient(models.Model):
    full_name = models.CharField(_("full_name"), max_length=100)
    pinfl = models.CharField(_("pinfl"), max_length=14)
    birth_date = models.DateField(_("birth_date"), null=True, blank=True)
    is_aggressive = models.BooleanField(_("is aggressive"), default=False)
    max_examination_interval = models.IntegerField(_("maximal examination interval (in days)"), default=30)
    neighborhood = models.ForeignKey(verbose_name=_("neighborhood"), to="utils.Neighborhood", on_delete=models.PROTECT, related_name="patients")
    inspector = models.ForeignKey(verbose_name=_("inspector"), to="utils.Inspector", on_delete=models.PROTECT, related_name="patients")
    psychiatrist = models.ForeignKey(verbose_name=_("psychiatrist"), to=Psychiatrist, on_delete=models.PROTECT, related_name="patients", null=True)
    address = models.CharField(_("address"), max_length=100, null=True, blank=True)
    last_psychiatric_appointment_date = models.DateField(_("date of the last psychiatric appointment"), null=True, blank=True)
    last_psychiatric_appointment_file = models.FileField(_("file of the last psychiatric appointment"), upload_to=upload_to_psychiatric_appointment_file, validators=file_validators, null=True, blank=True)
    last_home_visit_by_doctor_date = models.DateField(_("date of last home visit by a doctor or nurse"), null=True, blank=True)
    last_home_visit_by_doctor_file = models.FileField(_("file of last home visit by a doctor or nurse"), upload_to=upload_to_home_visit_by_doctor, validators=file_validators, null=True, blank=True)
    reason = models.CharField(_("if the patient has not been seen by a doctor within a month, the reason"), max_length=255, null=True, blank=True)
    receiving_supportive_therapy = models.CharField(_("receiving supportive therapy"), max_length=30, choices=ReceivingSupportiveTherapyChoices.choices, null=True, blank=True)
    reason_for_special_consideration = models.ForeignKey(verbose_name=_("reason for special consideration"), to=ReasonForSpecialConsideration, on_delete=models.SET_NULL, related_name="patients", null=True, blank=True)
    description_for_special_consideration = models.CharField(_("description for special consideration"), max_length=500, null=True, blank=True)
    social_domestic_environment = models.ForeignKey(verbose_name=_("social-domestic environment"), to=SocialDomesticEnvironment, on_delete=models.SET_NULL, related_name="patients", null=True, blank=True)
    alcohol_and_drug_use = models.CharField(_("alcohol and drug use"), max_length=30, choices=AlcoholAndDrugUse.choices, null=True, blank=True)
    where_is_now = models.CharField(_("where is now"), max_length=30, choices=WhereIsNow.choices, null=True, blank=True)
    description_where_is_now = models.CharField(_("description where is now"), max_length=500, null=True, blank=True)
    last_hospitalization_from = models.DateField(_("from date of last hospitalization"), null=True, blank=True)
    last_hospitalization_from_file = models.FileField(_("from date of last hospitalization file"), upload_to=upload_to_last_hospitalization_from, validators=file_validators, null=True, blank=True)
    last_hospitalization_to = models.DateField(_("to date of last hospitalization"), null=True, blank=True)
    last_hospitalization_to_file = models.FileField(_("to date of last hospitalization file"), upload_to=upload_to_last_hospitalization_to, validators=file_validators, null=True, blank=True)


    class Meta:
        verbose_name = _("Patient")
        verbose_name_plural = _("Patients")

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        if self.pk:
            old = Patient.objects.filter(pk=self.pk).first()
        else:
            old = None

        file_date_pairs = [
            ("last_psychiatric_appointment_file", "last_psychiatric_appointment_date"),
            ("last_home_visit_by_doctor_file", "last_home_visit_by_doctor_date"),
            ("last_hospitalization_from_file", "last_hospitalization_from"),
            ("last_hospitalization_to_file", "last_hospitalization_to"),
        ]

        for file_field, date_field in file_date_pairs:
            new_file = getattr(self, file_field)
            old_file = getattr(old, file_field) if old else None

            if new_file and (not old_file or new_file.name != old_file.name):
                setattr(self, date_field, datetime.date.today())

        if self.is_aggressive:
            if not (self.max_examination_interval and self.max_examination_interval <= 30):
                self.max_examination_interval = 30

        super().save(*args, **kwargs)






