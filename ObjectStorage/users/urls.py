from django.urls import path
from .views import  *
# from .views import RegisterView, ActivateView, LoginView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('activate/<uidb64>/<token>/', ActivateAccountView.as_view(), name='activate'),
    path('login/', LoginView.as_view(), name='login'),
    path("active/", ActivePageView.as_view(),name="active"),
    path('logout/', LogoutView.as_view(), name='logout'),


]
