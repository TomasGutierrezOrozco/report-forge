from django.contrib import admin
from .models import Machine, Evidence, Vulnerability, Exploit, Screenshot, Flag

@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ('name', 'platform', 'difficulty', 'operating_system', 'target_ip', 'status', 'created_at')
    list_filter = ('platform', 'difficulty', 'operating_system', 'status')
    search_fields = ('name', 'target_ip', 'author')

@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    list_display = ('title', 'machine', 'phase', 'order', 'created_at')
    list_filter = ('phase', 'machine')
    search_fields = ('title', 'command', 'explanation')
    ordering = ('machine', 'phase', 'order')

@admin.register(Vulnerability)
class VulnerabilityAdmin(admin.ModelAdmin):
    list_display = ('title', 'machine', 'vulnerability_type', 'severity', 'order', 'created_at')
    list_filter = ('severity', 'vulnerability_type', 'machine')
    search_fields = ('title', 'cve', 'affected_service')

@admin.register(Exploit)
class ExploitAdmin(admin.ModelAdmin):
    list_display = ('name', 'machine', 'exploit_type', 'objective', 'order', 'created_at')
    list_filter = ('exploit_type', 'objective', 'machine')
    search_fields = ('name', 'cve', 'affected_service')

@admin.register(Screenshot)
class ScreenshotAdmin(admin.ModelAdmin):
    list_display = ('id', 'machine', 'title', 'phase', 'order', 'created_at')
    list_filter = ('machine', 'phase')

@admin.register(Flag)
class FlagAdmin(admin.ModelAdmin):
    list_display = ('flag_type', 'machine', 'phase', 'censored', 'created_at')
    list_filter = ('flag_type', 'phase', 'censored', 'machine')
