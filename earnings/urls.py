from django.urls import path
from . import views

urlpatterns = [
    path('', views.earning_list, name='earning_list'),
    path('sort/', views.sort_earnings, name='sort_earnings'),
    path('add/', views.add_earning, name='add_earning'),
    path('add_details/<int:id>/', views.add_earning_details, name='add_earning_details'),
    path('details/<int:id>/', views.earning_list_details, name='earning_list_details'),
    path('delete/<int:pk>/', views.delete_earning, name='delete_earning'),
    path('register/', views.register, name='register'),
    path('earnings/edit/<int:pk>/', views.edit_earning, name='edit_earning'),
    path('earnings/export/', views.export_earnings_excel, name='export_earnings_excel'),
    path('delete/detail/<int:pk>/', views.delete_earning_detail, name='delete_earning_detail'),
    path('edit/detail/<int:pk>/', views.edit_earning_detail, name='edit_earning_detail'),
    path('import/', views.import_earnings, name='import_earnings'),
    path('edit-week/<int:id>/', views.update_weekly_pay, name='update_weekly_pay'),
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/add', views.add_invoice, name='add_invoice'),
    path('invoices/delete/<int:pk>/', views.delete_invoice, name='delete_invoice'),
    path('invoices/edit/<int:pk>/', views.edit_invoice, name='edit_invoice'),

]
