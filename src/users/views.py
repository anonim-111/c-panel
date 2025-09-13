from datetime import timedelta

from django.contrib import admin
from django.db.models import Count, Q, Case, When, Value, DateField, ExpressionWrapper, F, DurationField, BooleanField
from django.db.models.functions import Greatest
from django.shortcuts import render, redirect
from django.utils import timezone

from psytracks.models import Patient, Doctor, Psychiatrist
from utils.models import Neighborhood, Inspector, District


def dashboard_view(request):
    if not request.user.groups.filter(name__in=["Админ", "Бошлиқ", "Туман админи", "Вилоят админи"]).exists() and request.user.is_superuser is False:
        return redirect("/psytracks/patient/")

    user = request.user
    filter_q = Q(id__gte=0)
    inspector_filter_q = Q(id__gte=0)
    neighborhood_filter_q = Q(id__gte=0)
    if hasattr(user, "district"):
        filter_q &= Q(id=user.district.district_id)
        inspector_filter_q &= Q(neighborhood__district_id=user.district.district_id)
        neighborhood_filter_q &= Q(district_id=user.district.district_id)
    elif hasattr(user, "region"):
        filter_q &= Q(region_id=user.region.region_id)
        inspector_filter_q &= Q(neighborhood__district__region_id=user.region.region_id)
        neighborhood_filter_q &= Q(district__region_id=user.region.region_id)

    today = timezone.now().date()

    total_patient = Patient.objects.filter(inspector_filter_q).count()
    patients = Patient.objects.filter(inspector_filter_q).annotate(
            last_date=Case(
                When(
                    last_hospitalization_from__isnull=False,
                    last_hospitalization_to__isnull=False,
                    last_hospitalization_from__gt=F("last_hospitalization_to"),
                    then=Value(today)
                ),
                When(
                    last_hospitalization_from__isnull=False,
                    last_hospitalization_to__isnull=True,
                    then=Value(today)
                ),
                When(
                    last_hospitalization_from__isnull=True,
                    last_hospitalization_to__isnull=False,
                    then=Greatest(
                        "last_hospitalization_to",
                        "last_psychiatric_appointment_date",
                        "last_home_visit_by_doctor_date",
                    )
                ),
                When(
                    last_hospitalization_from__isnull=False,
                    last_hospitalization_to__isnull=False,
                    last_hospitalization_from__lte=F("last_hospitalization_to"),
                    then=Greatest(
                        "last_hospitalization_to",
                        "last_psychiatric_appointment_date",
                        "last_home_visit_by_doctor_date",
                    )
                ),
                When(
                    last_hospitalization_from__isnull=True,
                    last_hospitalization_to__isnull=True,
                    then=Greatest(
                        "last_psychiatric_appointment_date",
                        "last_home_visit_by_doctor_date",
                    )
                ),
                default=None,
                output_field=DateField()
            )
        ).annotate(
            interval=ExpressionWrapper(
                F("max_examination_interval") * Value(timedelta(days=1)),
                output_field=DurationField()
            ),
            deadline=ExpressionWrapper(
                F("last_date") + F("interval"),
                output_field=DateField()
            ),
            # deadline o‘tib ketganmi
            is_overdue=Case(
                When(last_date__isnull=True, then=Value(True)),
                When(deadline__lt=Value(today, output_field=DateField()), then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        )
    total_on_time_patient = patients.filter(is_overdue=False).count()
    total_late_patient = patients.filter(is_overdue=True).count()
    total_aggressive_on_time_patient = patients.filter(is_aggressive=True, is_overdue=False).count()
    total_aggressive_late_patient = patients.filter(is_aggressive=True, is_overdue=True).count()
    total_aggressive_patient = patients.filter(is_aggressive=True).count()
    total_neighborhood = Neighborhood.objects.filter(neighborhood_filter_q).count()
    total_doctor = Doctor.objects.filter(inspector_filter_q).count()
    total_psychiatrist = Psychiatrist.objects.filter(neighborhood_filter_q).count()
    total_inspector = Inspector.objects.filter(inspector_filter_q).count()

    districts = District.objects.filter(filter_q).annotate(
        late_count=Count(
            "neighborhoods__patients",
            filter=Q(neighborhoods__patients__in=patients.filter(is_overdue=True)),
            distinct=True,
        ),
        on_time_count=Count(
            "neighborhoods__patients",
            filter=Q(neighborhoods__patients__in=patients.filter(is_overdue=False)),
            distinct=True,
        ),
        aggressive_late_count=Count(
            "neighborhoods__patients",
            filter=Q(neighborhoods__patients__in=patients.filter(is_aggressive=True, is_overdue=True)),
            distinct=True,
        ),
        aggressive_on_time_count=Count(
            "neighborhoods__patients",
            filter=Q(neighborhoods__patients__in=patients.filter(is_aggressive=True, is_overdue=False)),
            distinct=True,
        ),
    )

    labels = []
    patients_list, aggressive_patients_list = [], []
    on_time, late = [], []
    aggressive_on_time, aggressive_late = [], []

    for d in districts:
        labels.append({"id": d.pk, "name": d.name})
        on_time.append(d.on_time_count)
        late.append(d.late_count)
        aggressive_on_time.append(d.aggressive_on_time_count)
        aggressive_late.append(d.aggressive_late_count)
        patients_list.append(d.on_time_count + d.late_count)
        aggressive_patients_list.append(d.aggressive_late_count + d.aggressive_on_time_count)

    context = {
        "total_patient": total_patient,
        "total_doctor": total_doctor,
        "total_psychiatrist": total_psychiatrist,
        "total_inspector": total_inspector,
        "total_neighborhood": total_neighborhood,
        "total_late_patient": total_late_patient,
        "total_on_time_patient": total_on_time_patient,
        "total_aggressive_patient": total_aggressive_patient,
        "total_aggressive_on_time_patient": total_aggressive_on_time_patient,
        "total_aggressive_late_patient": total_aggressive_late_patient,
        "district_labels": labels,
        "labels": [d["name"] for d in labels],
        "on_time": on_time,
        "late": late,
        "aggressive_on_time": aggressive_on_time,
        "aggressive_late": aggressive_late,
        "patients_list": patients_list,
        "aggressive_patients_list": aggressive_patients_list,
    }
    context.update(admin.site.each_context(request))
    return render(request, "admin/dashboard.html", context)


def statistics_view(request):
    if not request.user.groups.filter(name__in=["Админ", "Бошлиқ", "Туман админи", "Вилоят админи"]).exists() and request.user.is_superuser is False:
        return redirect("/psytracks/patient/")

    user = request.user
    filter_q = Q(id__gte=0)
    inspector_filter_q = Q(id__gte=0)
    neighborhood_filter_q = Q(id__gte=0)
    if hasattr(user, "district"):
        filter_q &= Q(id=user.district.district_id)
        inspector_filter_q &= Q(neighborhood__district_id=user.district.district_id)
        neighborhood_filter_q &= Q(district_id=user.district.district_id)
    elif hasattr(user, "region"):
        filter_q &= Q(region_id=user.region.region_id)
        inspector_filter_q &= Q(neighborhood__district__region_id=user.region.region_id)
        neighborhood_filter_q &= Q(district__region_id=user.region.region_id)

    today = timezone.now().date()
    total_patient = Patient.objects.filter(inspector_filter_q).count()
    patients = Patient.objects.filter(inspector_filter_q).annotate(
        last_date=Case(
            When(
                last_hospitalization_from__isnull=False,
                last_hospitalization_to__isnull=False,
                last_hospitalization_from__gt=F("last_hospitalization_to"),
                then=Value(today)
            ),
            When(
                last_hospitalization_from__isnull=False,
                last_hospitalization_to__isnull=True,
                then=Value(today)
            ),
            When(
                last_hospitalization_from__isnull=True,
                last_hospitalization_to__isnull=False,
                then=Greatest(
                    "last_hospitalization_to",
                    "last_psychiatric_appointment_date",
                    "last_home_visit_by_doctor_date",
                )
            ),
            When(
                last_hospitalization_from__isnull=False,
                last_hospitalization_to__isnull=False,
                last_hospitalization_from__lte=F("last_hospitalization_to"),
                then=Greatest(
                    "last_hospitalization_to",
                    "last_psychiatric_appointment_date",
                    "last_home_visit_by_doctor_date",
                )
            ),
            When(
                last_hospitalization_from__isnull=True,
                last_hospitalization_to__isnull=True,
                then=Greatest(
                    "last_psychiatric_appointment_date",
                    "last_home_visit_by_doctor_date",
                )
            ),
            default=None,
            output_field=DateField()
        )
    ).annotate(
        interval=ExpressionWrapper(
            F("max_examination_interval") * Value(timedelta(days=1)),
            output_field=DurationField()
        ),
        deadline=ExpressionWrapper(
            F("last_date") + F("interval"),
            output_field=DateField()
        ),
        # deadline o‘tib ketganmi
            is_overdue=Case(
                When(last_date__isnull=True, then=Value(True)),
                When(deadline__lt=Value(today, output_field=DateField()), then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
    )
    total_on_time_patient = patients.filter(is_overdue=False).count()
    total_late_patient = patients.filter(is_overdue=True).count()
    total_aggressive_on_time_patient = patients.filter(is_aggressive=True, is_overdue=False).count()
    total_aggressive_late_patient = patients.filter(is_aggressive=True, is_overdue=True).count()
    total_aggressive_patient = patients.filter(is_aggressive=True).count()
    total_neighborhood = Neighborhood.objects.filter(neighborhood_filter_q).count()
    total_doctor = Doctor.objects.filter(inspector_filter_q).count()
    total_psychiatrist = Psychiatrist.objects.filter(neighborhood_filter_q).count()
    total_inspector = Inspector.objects.filter(inspector_filter_q).count()

    districts = District.objects.filter(filter_q).annotate(
        late_count=Count(
            "neighborhoods__patients",
            filter=Q(neighborhoods__patients__in=patients.filter(is_overdue=True)),
            distinct=True,
        ),
        on_time_count=Count(
            "neighborhoods__patients",
            filter=Q(neighborhoods__patients__in=patients.filter(is_overdue=False)),
            distinct=True,
        ),
        aggressive_late_count=Count(
            "neighborhoods__patients",
            filter=Q(neighborhoods__patients__in=patients.filter(is_aggressive=True, is_overdue=True)),
            distinct=True,
        ),
        aggressive_on_time_count=Count(
            "neighborhoods__patients",
            filter=Q(neighborhoods__patients__in=patients.filter(is_aggressive=True, is_overdue=False)),
            distinct=True,
        ),
    )

    labels = []
    patients_list, aggressive_patients_list = [], []
    on_time, late = [], []
    aggressive_on_time, aggressive_late = [], []

    for d in districts:
        labels.append({"id": d.pk, "name": d.name})
        on_time.append(d.on_time_count)
        late.append(d.late_count)
        aggressive_on_time.append(d.aggressive_on_time_count)
        aggressive_late.append(d.aggressive_late_count)
        patients_list.append(d.on_time_count + d.late_count)
        aggressive_patients_list.append(d.aggressive_late_count + d.aggressive_on_time_count)

    context = {
        "total_patient": total_patient,
        "total_doctor": total_doctor,
        "total_psychiatrist": total_psychiatrist,
        "total_inspector": total_inspector,
        "total_neighborhood": total_neighborhood,
        "total_late_patient": total_late_patient,
        "total_on_time_patient": total_on_time_patient,
        "total_aggressive_patient": total_aggressive_patient,
        "total_aggressive_on_time_patient": total_aggressive_on_time_patient,
        "total_aggressive_late_patient": total_aggressive_late_patient,
        "district_labels": labels,
        "labels": [d["name"] for d in labels],
        "on_time": on_time,
        "late": late,
        "aggressive_on_time": aggressive_on_time,
        "aggressive_late": aggressive_late,
        "patients_list": patients_list,
        "aggressive_patients_list": aggressive_patients_list,
    }
    context.update(admin.site.each_context(request))
    return render(request, "admin/statistics.html", context)

