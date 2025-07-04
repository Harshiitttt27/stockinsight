# theme/views.py

from django.shortcuts import render

def register_page(request):
    return render(request, 'register.html')


def login_page(request):
    return render(request, 'login.html')



