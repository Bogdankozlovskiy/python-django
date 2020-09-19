from django.http import HttpResponse
from django.shortcuts import render


# def hello(request):
#     return HttpResponse("<h1>Hello world</h1>")

def hello(request):
    response = {"user": "Bogdan", "digit": 34.5}
    return render(request, "index.html", response)
