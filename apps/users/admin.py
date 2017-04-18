from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from apps.users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_active')
    readonly_fields = ('password', 'date_joined', 'last_login')
    fieldsets = (
        (None, {'fields': ('username', 'avatar', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
