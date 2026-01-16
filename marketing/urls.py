from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('features/', views.features, name='features'),
    path('pricing/', views.pricing, name='pricing'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
]
