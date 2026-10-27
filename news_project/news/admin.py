"""
Django Admin configuration for the News application.
Registers models with customized list views and filtering
options for administrators.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Publisher, Article, Newsletter


class CustomUserAdmin(UserAdmin):
    """Admin configuration for CustomUser incorporating
    role and subscription views."""
    model = CustomUser
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')

    # Extend default user fieldsets to include
    # custom role and m2m subscription fields
    fieldsets = UserAdmin.fieldsets + (
        ('Role & Subscriptions', {'fields': ('role',
                                             'subscriptions_publishers',
                                             'subscriptions_journalists')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role & Subscriptions', {'fields': ('role',
                                             'subscriptions_publishers',
                                             'subscriptions_journalists')}),
    )


class ArticleAdmin(admin.ModelAdmin):
    """Admin configuration for managing news articles and approval statuses."""
    list_display = ('title', 'publisher', 'journalist', 'approved', 'created_at')  # noqa: E501
    list_filter = ('approved', 'publisher', 'created_at')
    search_fields = ('title', 'content')
    list_editable = ('approved', 'publisher')


class PublisherAdmin(admin.ModelAdmin):
    """Admin configuration for publishing organizations."""
    list_display = ('name',)
    search_fields = ('name',)


class NewsletterAdmin(admin.ModelAdmin):
    """Admin configuration for compiled newsletters."""
    list_display = ('title', 'publisher', 'created_at')
    list_filter = ('publisher', 'created_at')
    search_fields = ('title', 'content')

# Register models with their custom admin views


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Publisher, PublisherAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Newsletter, NewsletterAdmin)
