# from django.urls import path
# from .views import  login_page, register_page

# urlpatterns = [
#     path('login/', login_page, name='login_page'),
#     path('register/', register_page, name='register_page'),
# ]
from django.urls import path
from .views import login_page, register_page
from .dashboard import dashboard_view

urlpatterns = [
    path('', register_page, name='register_page'),  # 👈 Root URL now shows register page
    path('login/', login_page, name='login_page'),
    path('register/', register_page, name='register_page'),
    path('dashboard/', dashboard_view, name='dashboard'),
   
]
