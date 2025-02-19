from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/',views.upload,name='upload'),
    path('upload/', views.upload_video, name='upload_video'),
    path('about/', views.about, name='about'),
    path('features/', views.features, name='features'),
    path('Sign Up/', views.register, name='register'),
    path('Sign in/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
]
