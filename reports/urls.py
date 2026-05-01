from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Machine URLs
    path('', views.machine_list, name='machine_list'),
    path('new/', views.machine_create, name='machine_create'),
    path('<int:pk>/', views.machine_detail, name='machine_detail'),
    path('<int:pk>/edit/', views.machine_edit, name='machine_edit'),
    path('<int:pk>/delete/', views.machine_delete, name='machine_delete'),

    # Evidence URLs
    path('<int:machine_id>/evidence/new/', views.evidence_create, name='evidence_create'),
    path('<int:machine_id>/evidence/<int:pk>/edit/', views.evidence_edit, name='evidence_edit'),
    path('<int:machine_id>/evidence/<int:pk>/delete/', views.evidence_delete, name='evidence_delete'),

    # Vulnerability URLs
    path('<int:machine_id>/vulnerabilities/new/', views.vulnerability_create, name='vulnerability_create'),
    path('<int:machine_id>/vulnerabilities/<int:pk>/edit/', views.vulnerability_edit, name='vulnerability_edit'),
    path('<int:machine_id>/vulnerabilities/<int:pk>/delete/', views.vulnerability_delete, name='vulnerability_delete'),

    # Exploit URLs
    path('<int:machine_id>/exploits/new/', views.exploit_create, name='exploit_create'),
    path('<int:machine_id>/exploits/<int:pk>/edit/', views.exploit_edit, name='exploit_edit'),
    path('<int:machine_id>/exploits/<int:pk>/delete/', views.exploit_delete, name='exploit_delete'),

    # Screenshot URLs
    path('<int:machine_id>/screenshots/new/', views.screenshot_create, name='screenshot_create'),
    path('<int:machine_id>/screenshots/<int:pk>/delete/', views.screenshot_delete, name='screenshot_delete'),

    # Flag URLs
    path('<int:machine_id>/flags/new/', views.flag_create, name='flag_create'),
    path('<int:machine_id>/flags/<int:pk>/edit/', views.flag_edit, name='flag_edit'),
    path('<int:machine_id>/flags/<int:pk>/delete/', views.flag_delete, name='flag_delete'),

    # Export URLs
    path('<int:machine_id>/export/', views.export_view, name='export_view'),
    path('<int:machine_id>/export/latex/', views.export_latex, name='export_latex'),
    path('<int:machine_id>/export/pdf/', views.export_pdf, name='export_pdf'),
    path('<int:machine_id>/export/markdown/', views.export_markdown, name='export_markdown'),
    path('<int:machine_id>/reorder/', views.reorder_items, name='reorder_items'),
]
