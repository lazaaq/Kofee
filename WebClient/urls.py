from django.urls import path
from . import views

app_name = 'WebClient'
urlpatterns = [
    path('input_image/', views.input_image, name='input_image'),
]