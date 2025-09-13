from datetime import timedelta

from django.db.models import Count, Q, Case, When, Value, F, DateField, ExpressionWrapper, DurationField, BooleanField
from django.db.models.functions import Greatest
from django.http import JsonResponse
from django.utils import timezone

from psytracks.models import Patient, Doctor, Psychiatrist
from utils.models import District, Neighborhood, Inspector


def district_patient_stats(request):
    user = request.user
    filter_q = Q(id__gte=0)
    if hasattr(user, "district"):
        filter_q &= Q(id=user.district.district_id)
    elif hasattr(user, "region"):
        filter_q &= Q(region_id=user.region.region_id)
    stats = (
        District.objects.filter(filter_q)
        .annotate(total=Count("neighborhoods__patients", distinct=True))
        .values("name", "id", "total")
    )
    return JsonResponse(list(stats), safe=False)


def mahalla_patient_stats(request, district_id):
    today = timezone.now().date()

    patients = Patient.objects.annotate(
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

    neighborhoods = Neighborhood.objects.filter(district_id=district_id).annotate(
        late_count=Count(
            "patients",
            filter=Q(patients__in=patients.filter(is_overdue=True)),
            distinct=True,
        ),
        on_time_count=Count(
            "patients",
            filter=Q(patients__in=patients.filter(is_overdue=False)),
            distinct=True,
        ),
        aggressive_late_count=Count(
            "patients",
            filter=Q(patients__in=patients.filter(is_aggressive=True, is_overdue=True)),
            distinct=True,
        ),
        aggressive_on_time_count=Count(
            "patients",
            filter=Q(patients__in=patients.filter(is_aggressive=True, is_overdue=False)),
            distinct=True,
        ),
    )
    labels = []
    patients_list, aggressive_patients_list = [], []
    on_time, late = [], []
    aggressive_on_time, aggressive_late = [], []

    for d in neighborhoods:
        labels.append(d.name)
        on_time.append(d.on_time_count)
        late.append(d.late_count)
        aggressive_on_time.append(d.aggressive_on_time_count)
        aggressive_late.append(d.aggressive_late_count)
        patients_list.append(d.on_time_count + d.late_count)
        aggressive_patients_list.append(d.aggressive_late_count + d.aggressive_on_time_count)

    data = {
        "labels": labels,
        "on_time": on_time,
        "late": late,
        "aggressive_on_time": aggressive_on_time,
        "aggressive_late": aggressive_late,
        "patients_list": patients_list,
        "aggressive_patients_list": aggressive_patients_list,
        "total_patient": Patient.objects.filter(neighborhood__district_id=district_id).count(),
        "total_neighborhood": neighborhoods.count(),
        "total_doctor": Doctor.objects.filter(neighborhood__district_id=district_id).count(),
        "total_psychiatrist": Psychiatrist.objects.filter(district_id=district_id).count(),
        "total_inspector": Inspector.objects.filter(neighborhood__district_id=district_id).count(),
        "total_aggressive_patient": Patient.objects.filter(
            neighborhood__district_id=district_id,
            is_aggressive=True,
        ).count(),
        "total_on_time_patient": patients.filter(
            neighborhood__district_id=district_id,
            is_overdue=False
        ).count(),
        "total_late_patient": patients.filter(
            neighborhood__district_id=district_id,
            is_overdue=True
        ).count(),
        "total_on_time_aggressive_patient": patients.filter(
            neighborhood__district_id=district_id,
            is_aggressive=True,
            is_overdue=False
        ).count(),
        "total_late_aggressive_patient": patients.filter(
            neighborhood__district_id=district_id,
            is_aggressive=True,
            is_overdue=True
        ).count()
    }
    return JsonResponse(data)
