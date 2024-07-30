from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import register, validate_otc

urlpatterns = [
    path('login/', LoginView.as_view(template_name='sign/login.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name='sign/logout.html'), name='logout'),
    path('signup/', register, name='signup'),
    path('validate_otc/<int:user_id>/', validate_otc, name='validate_otc'),
]