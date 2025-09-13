from dal import autocomplete

from utils.models import Inspector, Neighborhood
from .models import Psychiatrist


class PsychiatristAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Psychiatrist.objects.all()
        neighborhood_id = self.forwarded.get('neighborhood', None)
        neighborhood = Neighborhood.objects.filter(id=neighborhood_id).first()
        district_id = self.forwarded.get('district', None)
        if neighborhood:
            qs = qs.filter(district_id=neighborhood.district_id)
        if district_id:
            qs = qs.filter(district_id=district_id)
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs


class InspectorAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Inspector.objects.all()
        neighborhood_id = self.forwarded.get('neighborhood', None)
        district_id = self.forwarded.get('district', None)
        if neighborhood_id:
            qs = qs.filter(neighborhood_id=neighborhood_id)
        if district_id:
            qs = qs.filter(neighborhood__district_id=district_id)
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs