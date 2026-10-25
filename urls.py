from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from vault import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("register/", views.register, name="register"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", views.dashboard, name="dashboard"),
    path("upload/", views.upload_document, name="upload"),
    path("documents/<int:pk>/download/", views.download_document, name="download"),
    path("documents/<int:pk>/share/", views.share_document, name="share"),
    path("documents/<int:pk>/edit/", views.edit_document, name="edit_document"),
    path("documents/<int:pk>/shares/<int:share_id>/revoke/", views.revoke_share, name="revoke_share"),
    path("audit/", views.audit_trail, name="audit"),
]
