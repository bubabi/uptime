from django.contrib import admin

from monitor.models import Monitor


@admin.register(Monitor)
class MonitorAdmin(admin.ModelAdmin):
    list_display = ('user', 'url', 'interval', 'status', 'checked_at', 'created_at', 'is_active')
    list_filter = ('is_active', 'status', 'interval', 'checked_at')
    date_hierarchy = 'created_at'
    search_fields = ('user__first_name', 'user__last_name', 'user__username', 'user__email', 'url',)
    raw_id_fields = ('user',)