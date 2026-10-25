from pathlib import Path
import uuid
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.utils import timezone

private_storage = FileSystemStorage(location=settings.PRIVATE_MEDIA_ROOT)

def private_upload_path(instance, filename):
    suffix = Path(filename).suffix.lower()[:12]
    return f"user_{instance.owner_id}/{timezone.now():%Y/%m}/{uuid.uuid4().hex}{suffix}"

class Document(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="vault_documents")
    title = models.CharField(max_length=160)
    file = models.FileField(upload_to=private_upload_path, storage=private_storage)
    original_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    size_bytes = models.PositiveBigIntegerField(default=0)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.title

class DocumentShare(models.Model):
    READ = "READ"
    EDIT = "EDIT"
    PERMISSION_CHOICES = [(READ, "Read only"), (EDIT, "Edit")]
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="shares")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="document_shares")
    permission = models.CharField(max_length=4, choices=PERMISSION_CHOICES, default=READ)
    granted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="granted_document_shares")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["document", "user"], name="unique_document_share_user")]
        ordering = ["user__username"]

    def __str__(self):
        return f"{self.document} → {self.user} ({self.permission})"

class AuditEvent(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    document = models.ForeignKey(Document, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=40)
    details = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} — {self.created_at:%Y-%m-%d %H:%M}"
