from django.contrib import admin
from .models import AuditEvent, Document, DocumentShare

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "original_name", "size_bytes", "uploaded_at")
    search_fields = ("title", "original_name", "owner__username")
    readonly_fields = ("uploaded_at", "size_bytes", "original_name")

@admin.register(DocumentShare)
class DocumentShareAdmin(admin.ModelAdmin):
    list_display = ("document", "user", "permission", "granted_by", "created_at", "updated_at")
    list_filter = ("permission", "created_at")
    search_fields = ("document__title", "user__username", "granted_by__username")
    readonly_fields = ("created_at", "updated_at")

@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("action", "actor", "document", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("actor__username", "document__title", "details")
    readonly_fields = ("actor", "document", "action", "details", "created_at")
