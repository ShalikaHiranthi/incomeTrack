from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_gigwork, name='add_gigwork'),
    path('', views.gigwork_list, name='gigwork_list'),
    path('edit/<int:id>/', views.gigwork_edit, name='gigwork_edit'),
    path('delete/<int:id>/', views.gigwork_delete, name='gigwork_delete'),
    path('import/', views.import_gigwork, name='import_gigwork'),
    path('export/', views.export_gigs_excel, name='export_gigs_excel'),
    path('sort/', views.sort_gigs, name='sort_gigs'),
    path('edit-week/<int:id>/', views.update_weekly_earning, name='update_weekly_earning'),
    path('invoices/', views.payment_list, name='payment_list'),
    path('invoices/add', views.add_invoice, name='add_invoice'),
    path('invoices/delete/<int:pk>/', views.delete_invoice, name='delete_invoice'),
    path('invoices/edit/<int:pk>/', views.edit_invoice, name='edit_invoice'),
]
