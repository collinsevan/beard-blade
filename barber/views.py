from django.shortcuts import render   # noqa: F401
from django.http import HttpResponse


# Create your views here.
def home(request):
    return HttpResponse("Welcome to the Barber Booking site!")
