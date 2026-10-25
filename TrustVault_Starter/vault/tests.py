from tempfile import TemporaryDirectory

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from .models import AuditEvent, Document, DocumentShare, private_storage

class DocumentAccessTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.private_media_directory = TemporaryDirectory()
        cls.original_private_media_location = private_storage.location
        private_storage.location = cls.private_media_directory.name

    @classmethod
    def tearDownClass(cls):
        private_storage.location = cls.original_private_media_location
        cls.private_media_directory.cleanup()
        super().tearDownClass()

    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="Strong-test-pass-123")
        self.reader = User.objects.create_user(username="reader", password="Strong-test-pass-123")
        self.editor = User.objects.create_user(username="editor", password="Strong-test-pass-123")
        self.document = Document.objects.create(
            owner=self.owner, title="Test report", original_name="report.txt", size_bytes=11,
            file=SimpleUploadedFile("report.txt", b"hello world", content_type="text/plain"),
        )

    def test_unshared_user_cannot_download(self):
        self.client.force_login(self.reader)
        response = self.client.get(reverse("download", args=[self.document.pk]))
        self.assertEqual(response.status_code, 404)

    def test_read_user_can_download_but_cannot_edit_metadata(self):
        DocumentShare.objects.create(document=self.document, user=self.reader, permission=DocumentShare.READ, granted_by=self.owner)
        self.client.force_login(self.reader)
        response = self.client.get(reverse("download", args=[self.document.pk]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("edit_document", args=[self.document.pk]))
        self.assertEqual(response.status_code, 403)

    def test_edit_user_can_update_title(self):
        DocumentShare.objects.create(document=self.document, user=self.editor, permission=DocumentShare.EDIT, granted_by=self.owner)
        self.client.force_login(self.editor)
        response = self.client.post(reverse("edit_document", args=[self.document.pk]), {"title": "Updated report"})
        self.assertEqual(response.status_code, 302)
        self.document.refresh_from_db()
        self.assertEqual(self.document.title, "Updated report")
        self.assertTrue(AuditEvent.objects.filter(action="DOCUMENT_EDIT", actor=self.editor).exists())

    def test_owner_can_grant_and_revoke_access(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse("share", args=[self.document.pk]), {"username": "reader", "permission": "READ"})
        self.assertEqual(response.status_code, 302)
        share = DocumentShare.objects.get(document=self.document, user=self.reader)
        response = self.client.post(reverse("revoke_share", args=[self.document.pk, share.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(DocumentShare.objects.filter(pk=share.pk).exists())
        # Revocation must block the recipient's next request, not merely hide a button.
        self.client.force_login(self.reader)
        denied = self.client.get(reverse("download", args=[self.document.pk]))
        self.assertEqual(denied.status_code, 404)
        self.assertTrue(AuditEvent.objects.filter(action="ACCESS_REVOKED", actor=self.owner).exists())

    def test_non_owner_cannot_manage_shares(self):
        DocumentShare.objects.create(document=self.document, user=self.reader, permission=DocumentShare.EDIT, granted_by=self.owner)
        self.client.force_login(self.reader)
        self.assertEqual(self.client.get(reverse("share", args=[self.document.pk])).status_code, 404)

    def test_registration_creates_account_and_signs_user_in(self):
        response = self.client.post(reverse("register"), {
            "username": "new-member",
            "email": "new-member@example.test",
            "password1": "Vault-Unit-Test-Strong-927!",
            "password2": "Vault-Unit-Test-Strong-927!",
        })
        self.assertRedirects(response, reverse("dashboard"))
        self.assertTrue(User.objects.filter(username="new-member").exists())
        self.assertEqual(self.client.get(reverse("dashboard")).status_code, 200)

    def test_login_authenticates_existing_user(self):
        password = "Vault-Login-Test-Strong-927!"
        self.owner.set_password(password)
        self.owner.save()
        response = self.client.post(reverse("login"), {"username": "owner", "password": password})
        self.assertRedirects(response, reverse("dashboard"))
        self.assertEqual(self.client.get(reverse("dashboard")).status_code, 200)

    def test_upload_download_and_share_actions_are_audited(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse("upload"), {
            "title": "Audit report",
            "file": SimpleUploadedFile("audit.txt", b"private report", content_type="text/plain"),
        })
        self.assertRedirects(response, reverse("dashboard"))
        document = Document.objects.get(title="Audit report")
        self.assertTrue(AuditEvent.objects.filter(document=document, action="DOCUMENT_UPLOAD").exists())

        response = self.client.get(reverse("download", args=[document.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(AuditEvent.objects.filter(document=document, action="DOCUMENT_DOWNLOAD").exists())

        response = self.client.post(reverse("share", args=[document.pk]), {
            "username": self.reader.username,
            "permission": DocumentShare.READ,
        })
        self.assertRedirects(response, reverse("share", args=[document.pk]))
        self.assertTrue(AuditEvent.objects.filter(document=document, action="ACCESS_GRANTED").exists())

        response = self.client.get(reverse("audit"))
        self.assertContains(response, "DOCUMENT_UPLOAD")
        self.assertContains(response, "DOCUMENT_DOWNLOAD")
        self.assertContains(response, "ACCESS_GRANTED")

    def test_upload_rejects_disallowed_extension(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse("upload"), {
            "title": "Unexpected file",
            "file": SimpleUploadedFile("payload.exe", b"not an executable", content_type="application/octet-stream"),
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Document.objects.filter(title="Unexpected file").exists())

    def test_upload_rejects_files_over_10_mb(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse("upload"), {
            "title": "Oversized file",
            "file": SimpleUploadedFile("large.txt", b"x" * (10 * 1024 * 1024 + 1), content_type="text/plain"),
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Document.objects.filter(title="Oversized file").exists())
