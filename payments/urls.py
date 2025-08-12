from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('payment/<int:booking_id>/', views.PaymentView.as_view(), name='payment'),
    path('manual/<int:booking_id>/', views.ManualPaymentView.as_view(), name='manual_payment'),
    path('manual/<int:booking_id>/status/', views.ManualPaymentStatusView.as_view(), name='manual_payment_status'),
    path('create-payment-intent/', views.CreatePaymentIntentView.as_view(), name='create_payment_intent'),
    path('webhook/', views.StripeWebhookView.as_view(), name='stripe_webhook'),
    path('success/', views.PaymentSuccessView.as_view(), name='payment_success'),
    path('cancel/', views.PaymentCancelView.as_view(), name='payment_cancel'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('check-payment-status/', views.check_payment_status, name='check_payment_status'),
]
