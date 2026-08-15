from django.shortcuts import render


def homepage(request):
    return render(request, "homepage.html")


def inquiry_page(request):
    return render(request, "inquiry.html")
