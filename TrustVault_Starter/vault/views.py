from pathlib import Path
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import get_valid_filename
from .forms import DocumentUploadForm, RegistrationForm, ShareDocumentForm, EditDocumentForm
from .models import AuditEvent, Document, DocumentShare

@login_required
def dashboard(request):
    owned = Document.objects.filter(owner=request.user)
    shared = Document.objects.filter(shares__user=request.user).exclude(owner=request.user)
    documents = (owned | shared).distinct().select_related("owner")
    for doc in documents:
        doc.is_owner = doc.owner_id == request.user.id
        share = DocumentShare.objects.filter(document=doc, user=request.user).first() if not doc.is_owner else None
        doc.my_permission = "OWNER" if doc.is_owner else (share.permission if share else "READ")
    return render(request, "dashboard.html", {"documents": documents, "total": documents.count()})

@login_required
def upload_document(request):
    if request.method == "POST":
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded = request.FILES.get("file")
            if not uploaded:
                form.add_error("file", "Choose a file to upload.")
            elif uploaded.size > 10 * 1024 * 1024:
                form.add_error("file", "Files must be 10 MB or smaller.")
            else:
                doc = form.save(commit=False)
                doc.owner = request.user
                doc.original_name = get_valid_filename(uploaded.name)[:255]
                doc.size_bytes = uploaded.size
                doc.save()
                AuditEvent.objects.create(actor=request.user, document=doc, action="DOCUMENT_UPLOAD", details=doc.original_name)
                messages.success(request, "Document uploaded securely.")
                return redirect("dashboard")
    else:
        form = DocumentUploadForm()
    return render(request, "upload.html", {"form": form})

def get_accessible_document(user, pk):
    doc = get_object_or_404(Document.objects.select_related("owner"), pk=pk)
    if doc.owner_id == user.id:
        return doc, "OWNER"
    share = DocumentShare.objects.filter(document=doc, user=user).first()
    if not share:
        raise Http404("Document not found.")
    return doc, share.permission

@login_required
def download_document(request, pk):
    doc, permission = get_accessible_document(request.user, pk)
    if permission not in ("OWNER", DocumentShare.READ, DocumentShare.EDIT):
        raise Http404("Document not found.")
    try:
        file_handle = doc.file.open("rb")
    except (FileNotFoundError, ValueError, OSError):
        raise Http404("Stored file not found.")
    AuditEvent.objects.create(actor=request.user, document=doc, action="DOCUMENT_DOWNLOAD", details=f"Downloaded {doc.original_name}")
    return FileResponse(file_handle, as_attachment=True, filename=doc.original_name)

@login_required
def share_document(request, pk):
    doc = get_object_or_404(Document, pk=pk, owner=request.user)
    if request.method == "POST":
        form = ShareDocumentForm(request.POST)
        if form.is_valid():
            recipient = form.recipient
            if recipient.pk == request.user.pk:
                form.add_error("username", "You already own this document.")
            else:
                permission = form.cleaned_data["permission"]
                with transaction.atomic():
                    share, created = DocumentShare.objects.update_or_create(
                        document=doc, user=recipient,
                        defaults={"permission": permission, "granted_by": request.user},
                    )
                    action = "ACCESS_GRANTED" if created else "ACCESS_UPDATED"
                    AuditEvent.objects.create(actor=request.user, document=doc, action=action, details=f"{permission} access for {recipient.username}")
                messages.success(request, f"{permission} access {'granted' if created else 'updated'} for {recipient.username}.")
                return redirect("share", pk=doc.pk)
    else:
        form = ShareDocumentForm()
    shares = doc.shares.select_related("user", "granted_by")
    return render(request, "share.html", {"document": doc, "form": form, "shares": shares})

@login_required
def revoke_share(request, pk, share_id):
    if request.method != "POST":
        raise Http404
    doc = get_object_or_404(Document, pk=pk, owner=request.user)
    share = get_object_or_404(DocumentShare, pk=share_id, document=doc)
    username = share.user.username
    share.delete()
    AuditEvent.objects.create(actor=request.user, document=doc, action="ACCESS_REVOKED", details=f"Access revoked for {username}")
    messages.success(request, f"Access revoked for {username}.")
    return redirect("share", pk=doc.pk)

@login_required
def edit_document(request, pk):
    doc, permission = get_accessible_document(request.user, pk)
    if permission not in ("OWNER", DocumentShare.EDIT):
        raise PermissionDenied("You have read-only access to this document.")
    if request.method == "POST":
        form = EditDocumentForm(request.POST, instance=doc)
        if form.is_valid():
            form.save()
            AuditEvent.objects.create(actor=request.user, document=doc, action="DOCUMENT_EDIT", details="Updated document title")
            messages.success(request, "Document details updated.")
            return redirect("dashboard")
    else:
        form = EditDocumentForm(instance=doc)
    return render(request, "edit_document.html", {"document": doc, "form": form})

@login_required
def audit_trail(request):
    # Show events for documents the user owns or can currently access, plus events they performed.
    accessible_ids = Document.objects.filter(owner=request.user).values_list("id", flat=True)
    shared_ids = DocumentShare.objects.filter(user=request.user).values_list("document_id", flat=True)
    events = AuditEvent.objects.filter(document_id__in=list(accessible_ids) + list(shared_ids)).select_related("actor", "document").order_by("-created_at")[:200]
    return render(request, "audit.html", {"events": events})

def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your TrustVault account has been created.")
            return redirect("dashboard")
    else:
        form = RegistrationForm()
    return render(request, "register.html", {"form": form})
