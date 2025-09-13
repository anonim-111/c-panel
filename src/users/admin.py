from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from .models import User, RegionAdmin, DistrictAdmin

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (_('General'), {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'telegram_id')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )
    list_display = ('username', 'email', 'telegram_id', 'is_staff')
    search_fields = ('username__icontains', 'email', 'telegram_id')
    ordering = ('username',)

    def save_model(self, request, obj, form, change):
        """
        Agar admin paneldan parol oddiy matnda kiritilgan bo'lsa,
        set_password orqali hash qilib saqlaymiz.
        """
        if form.cleaned_data.get("password"):
            raw_password = form.cleaned_data["password"]
            if not raw_password.startswith("pbkdf2_"):  # oldindan hash bo'lmagan bo'lsa
                obj.set_password(raw_password)
        super().save_model(request, obj, form, change)


admin.site.unregister(Group)

@admin.register(Group)
class CustomGroupAdmin(admin.ModelAdmin):
    list_display = ("name",)
    filter_horizontal = ("permissions",)


@admin.register(RegionAdmin)
class RegionAdminAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "region")


@admin.register(DistrictAdmin)
class DistrictAdminAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "district")

