from django.shortcuts import render, redirect


# Create your views here.


def home_view(request):
    context = {}
    return render(request, 'homepage/home.html', context)


def faq_view(request):
    context = {}
    return render(request, 'homepage/faq.html', context)


def about_view(request):
    context = {}
    return render(request, 'homepage/about.html', context)


def services_view(request):
    context = {}
    return render(request, 'homepage/services.html', context)
