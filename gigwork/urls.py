from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_gigwork, name='add_gigwork'),
    path('', views.gigwork_list, name='gigwork_list'),
    path('gigwork/edit/<int:id>/', views.gigwork_edit, name='gigwork_edit'),
    path('gigwork/delete/<int:id>/', views.gigwork_delete, name='gigwork_delete'),
    path('gigwork/import/', views.import_gigwork, name='import_gigwork'),
]
