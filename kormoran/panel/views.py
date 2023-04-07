from django.http import HttpResponse
from django.shortcuts import redirect, render


def index(request):
    return HttpResponse("<h1> Sieeeemaaaa koleżankooooo </h1>")
