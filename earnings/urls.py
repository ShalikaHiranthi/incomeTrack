from django.urls import path
from . import views

urlpatterns = [
    path('', views.earning_list, name='earning_list'),
    path('sort/', views.earning_list_sort, name='earning_list_sort'),
    path('add/', views.add_earning, name='add_earning'),
    path('add_details/<int:id>/', views.add_earning_details, name='add_earning_details'),
    path('details/<int:id>/', views.earning_list_details, name='earning_list_details'),
    path('delete/<int:pk>/', views.delete_earning, name='delete_earning'),
    path('register/', views.register, name='register'),
    path('earnings/edit/<int:pk>/', views.edit_earning, name='edit_earning'),
    path('earnings/export/', views.export_earnings_excel, name='export_earnings_excel'),
    path('delete/detail/<int:pk>/', views.delete_earning_detail, name='delete_earning_detail'),
    path('edit/detail/<int:pk>/', views.edit_earning_detail, name='edit_earning_detail'),

]
