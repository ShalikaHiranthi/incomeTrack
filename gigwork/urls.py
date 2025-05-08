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
]
