# theme/views.py

from django.shortcuts import render

def register_page(request):
    return render(request, 'register.html')


def login_page(request):
    return render(request, 'login.html')


def tailwind_test(request):
    return render(request, 'test_tailwind.html')
