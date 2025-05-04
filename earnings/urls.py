from django.urls import path
from . import views

urlpatterns = [
    path('', views.earning_list, name='earning_list'),
    path('add/', views.add_earning, name='add_earning'),
    path('delete/<int:pk>/', views.delete_earning, name='delete_earning'),
    path('register/', views.register, name='register'),
]
