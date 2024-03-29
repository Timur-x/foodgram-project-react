from django.contrib.admin import ModelAdmin, register
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import Subscription, User


@register(User)
class UserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = (
        'email', 'id', 'username', 'first_name', 'last_name', 'is_blocked',
        'is_superuser',
    )
    list_filter = (
        'email', 'username', 'is_blocked', 'is_superuser',
    )
    fieldsets = (
        (None, {'fields': (
            'email', 'username', 'first_name', 'last_name', 'password',
        )}),
        ('Permissions', {'fields': ('is_blocked', 'is_superuser',)})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'username', 'first_name', 'last_name', 'password1',
                'password2', 'is_blocked', 'is_superuser',
            )
        }),
    )
    search_fields = ('email', 'username', 'first_name', 'last_name',)
    ordering = ('email', 'id', 'username',)


@register(Subscription)
class SubscriptionAdmin(ModelAdmin):
    list_display = ('id', 'user', 'author')
    search_fields = ('user', 'author')
