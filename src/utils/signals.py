from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

def create_virtual_permissions(sender, **kwargs):
    content_type, _ = ContentType.objects.get_or_create(
        app_label="utils",
        model="virtual"
    )
    Permission.objects.get_or_create(
        codename="view_statistics",
        name="Can view statistics page",
        content_type=content_type,
    )
