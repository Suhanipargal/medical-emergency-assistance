from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('login/', views.LoginPage, name='login'),
    path('', views.SignupPage, name='signup'),
    path('logout/', views.LogoutPage, name='logout'),
    path('help_map/', views.HelpMapPage, name='help_map'),
    path('provide-help/', views.provide_help, name='provide_help'),
    path('show_route/', views.show_route, name='show_route')
]
