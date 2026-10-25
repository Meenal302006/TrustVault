from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from pathlib import Path
from .models import Document, DocumentShare

class DocumentUploadForm(forms.ModelForm):
    ALLOWED_EXTENSIONS = {".pdf", ".txt", ".doc", ".docx", ".csv", ".png", ".jpg", ".jpeg"}

    def clean_file(self):
        uploaded = self.cleaned_data.get("file")
        if uploaded:
            suffix = Path(uploaded.name).suffix.lower()
            if suffix not in self.ALLOWED_EXTENSIONS:
                raise forms.ValidationError("Unsupported file type. Allowed: PDF, TXT, DOC, DOCX, CSV, PNG, JPG, JPEG.")
            if uploaded.size > 10 * 1024 * 1024:
                raise forms.ValidationError("Files must be 10 MB or smaller.")
        return uploaded

    class Meta:
        model = Document
        fields = ["title", "file"]
        widgets = {"title": forms.TextInput(attrs={"placeholder": "e.g. Internship Report", "maxlength": 160})}

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Use an email address you can access.")
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2")
    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

class ShareDocumentForm(forms.Form):
    username = forms.CharField(max_length=150, label="Recipient username")
    permission = forms.ChoiceField(choices=DocumentShare.PERMISSION_CHOICES, widget=forms.Select())
    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        try:
            self.recipient = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            raise forms.ValidationError("No registered user has that username.")
        return self.recipient.username

class EditDocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["title"]
