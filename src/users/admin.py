from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'telegram_id')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'telegram_id'),
        }),
    )
    list_display = ('username', 'email', 'telegram_id', 'is_staff')
    search_fields = ('username', 'email', 'telegram_id')
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