from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('verification/', views.SellerVerificationView.as_view(), name='seller_verification'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('seller-contract/', views.seller_contract, name='seller_contract'),
    path('seller-pending/', views.seller_pending, name='seller_pending'),
    # Password reset
    path('password-reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    # Google login
    path('google-login/', views.GoogleLoginView.as_view(), name='google_login'),
]
