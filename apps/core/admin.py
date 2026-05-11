from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

User = get_user_model()

admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Custom admin for User model."""
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    
    # Add these to make the admin fields editable inline
    add_fieldsets = (  # For user creation form
        (None, {
            'fields': ('username', 'password', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'is_superuser')
        }),
    )
    
    # Removed the duplicate fieldsets addition
