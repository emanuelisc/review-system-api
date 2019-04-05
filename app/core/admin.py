from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _

from core import models


class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('name', )}),
        (
            _('Permissions'),
            {
                'fields': ('is_active', 'is_staff', 'is_superuser')
            }
        ),
        (_('Important dates'), {'fields': ('last_login',)})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Page)
admin.site.register(models.PageCategory)
admin.site.register(models.Provider)
admin.site.register(models.ProviderService)
admin.site.register(models.Ticket)
admin.site.register(models.Review)
admin.site.register(models.RatingLog)
admin.site.register(models.ReviewCategory)
admin.site.register(models.HashTag)
admin.site.register(models.Comment)
