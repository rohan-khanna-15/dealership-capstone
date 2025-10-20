from django.urls import path
from . import views

app_name = 'djangoapp'

urlpatterns = [
    path('', views.get_dealerships, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.login_request, name='login'),
    path('logout/', views.logout_request, name='logout'),
    path('registration/', views.registration_request, name='registration'),
]
