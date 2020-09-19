from django.urls import path

from managebook import views

# hello/
urlpatterns = [
    path('hello/', views.hello, name="hello"),
]
