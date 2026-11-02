from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('produtos/', views.produtos, name='produtos'),
    path('movimentar/', views.movimentar, name='movimentar'),
    path('historico/', views.historico, name='historico'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]