import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
import vault.models

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(name="Document", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("title", models.CharField(max_length=160)),
            ("file", models.FileField(storage=vault.models.private_storage, upload_to="vault.models.private_upload_path")),
            ("original_name", models.CharField(max_length=255)),
            ("uploaded_at", models.DateTimeField(auto_now_add=True)),
            ("size_bytes", models.PositiveBigIntegerField(default=0)),
            ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="vault_documents", to=settings.AUTH_USER_MODEL)),
        ], options={"ordering": ["-uploaded_at"]}),
        migrations.CreateModel(name="AuditEvent", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("action", models.CharField(max_length=40)),
            ("details", models.CharField(blank=True, max_length=255)),
            ("created_at", models.DateTimeField(auto_now_add=True)),
            ("actor", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ("document", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="vault.document")),
        ], options={"ordering": ["-created_at"]}),
        migrations.CreateModel(name="DocumentShare", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("permission", models.CharField(choices=[("READ", "Read only"), ("EDIT", "Edit")], default="READ", max_length=4)),
            ("created_at", models.DateTimeField(auto_now_add=True)),
            ("updated_at", models.DateTimeField(auto_now=True)),
            ("document", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="shares", to="vault.document")),
            ("granted_by", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="granted_document_shares", to=settings.AUTH_USER_MODEL)),
            ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="document_shares", to=settings.AUTH_USER_MODEL)),
        ], options={"ordering": ["user__username"]}),
        migrations.AddConstraint(model_name="documentshare", constraint=models.UniqueConstraint(fields=("document", "user"), name="unique_document_share_user")),
    ]
