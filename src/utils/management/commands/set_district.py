import json
from django.core.management.base import BaseCommand
from utils.models import District, Neighborhood

class Command(BaseCommand):
    help = "Load district and neighborhood names from JSON file"

    def handle(self, *args, **options):

        with open("districts.json", encoding="utf-8") as f:
            data = json.load(f)

        for name in data.keys():
            district = District.objects.create(name=name, region_id=1)
            for neighborhood in data[name]:
                Neighborhood.objects.create(name=neighborhood, district=district)

        self.stdout.write(self.style.SUCCESS("District and neighborhood data loaded successfully!"))
