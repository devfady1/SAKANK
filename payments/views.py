import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from bookings.models import Booking

@csrf_exempt
def create_checkout_session(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    import json
    data = json.loads(request.body)
    booking_id = data.get('booking_id')
    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return JsonResponse({'error': 'الحجز غير موجود'}, status=404)
    if not hasattr(booking, 'total_amount') or booking.total_amount is None or booking.total_amount <= 0:
        return JsonResponse({'error': 'سعر الحجز غير صحيح'}, status=400)

    # Enhanced: validate and set Stripe secret key, with logging
    import logging
    logger = logging.getLogger('payments')
    secret = (settings.STRIPE_SECRET_KEY or '').strip().strip('"').strip("'")
    if not secret or not secret.startswith('sk_'):
        logger.error("Stripe SECRET key invalid or quoted. Raw value: %r", settings.STRIPE_SECRET_KEY)
        return JsonResponse({'error': 'Stripe secret key is invalid. تأكد من إزالة علامات الاقتباس من .env وأعد تشغيل السيرفر.'}, status=500)

    try:
        stripe.api_key = secret
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'egp',
                    'product_data': {
                        'name': f'حجز رقم {booking.id}',
                    },
                    'unit_amount': int(float(booking.total_amount) * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri('/payments/success/') + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri('/payments/cancel/'),
            metadata={'booking_id': booking.id},
        )
        return JsonResponse({'session_url': session.url})
    except Exception as e:
        logger.exception("Stripe checkout session creation failed (booking_id=%s)", booking_id)
        return JsonResponse({'error': str(e)}, status=500)

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
import stripe
import json
import logging
from bookings.models import Booking
from .models import Payment, WebhookEvent, ManualPayment
from .forms import ManualPaymentForm

# إعداد logger
logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentView(LoginRequiredMixin, TemplateView):
    """صفحة الدفع"""
    template_name = 'payments/payment.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking_id = kwargs['booking_id']
        booking = get_object_or_404(Booking, id=booking_id, user=self.request.user)
        
        context.update({
            'booking': booking,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'manual_payment_url': f"/payments/manual/{booking.id}/",
        })
        return context


class CreatePaymentIntentView(LoginRequiredMixin, View):
    """إنشاء نية الدفع في Stripe"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            booking_id = data.get('booking_id')
            
            booking = get_object_or_404(Booking, id=booking_id, user=request.user)
            
            # إنشاء نية الدفع
            intent = stripe.PaymentIntent.create(
                amount=int(booking.total_amount * 100),  # تحويل للقرش
                currency='egp',
                metadata={
                    'booking_id': booking.id,
                    'user_id': request.user.id,
                }
            )
            
            # حفظ معلومات الدفع
            payment, created = Payment.objects.get_or_create(
                booking=booking,
                defaults={
                    'stripe_payment_intent_id': intent.id,
                    'amount': booking.total_amount,
                    'currency': 'EGP',
                }
            )
            
            return JsonResponse({
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id,
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(View):
    """معالج Webhook من Stripe"""
    
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError:
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError:
            return HttpResponse(status=400)
        
            # تحديث حالة الحجز عند نجاح الدفع عبر Stripe Checkout
            if event['type'] == 'checkout.session.completed':
                session = event['data']['object']
                booking_id = session.get('metadata', {}).get('booking_id')
                if booking_id:
                    try:
                        booking = Booking.objects.get(id=booking_id)
                        booking.payment_status = 'paid'
                        booking.status = 'confirmed'
                        booking.save()
                    except Booking.DoesNotExist:
                        pass
        
        # حفظ الحدث
        webhook_event, created = WebhookEvent.objects.get_or_create(
            stripe_event_id=event['id'],
            defaults={
                'event_type': event['type'],
                'data': event['data'],
            }
        )
        
        if created:
            # معالجة الحدث
            if event['type'] == 'payment_intent.succeeded':
                self._handle_payment_success(event['data']['object'])
            elif event['type'] == 'payment_intent.payment_failed':
                self._handle_payment_failed(event['data']['object'])
            
            webhook_event.processed = True
            webhook_event.save()
        
        return HttpResponse(status=200)


class ManualPaymentView(LoginRequiredMixin, View):
    """الدفع اليدوي عبر فودافون كاش: عرض التعليمات وتسجيل إثبات الدفع"""

    VODAFONE_CASH_RECEIVER = "01069476417"

    def get(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        # في حال سبق التسجيل، اعرض الحالة
        instance = getattr(booking, 'manual_payment', None)
        form = ManualPaymentForm(instance=None)
        return render(request, 'payments/manual_payment.html', {
            'booking': booking,
            'form': form,
            'receiver_number': self.VODAFONE_CASH_RECEIVER,
            'instance': instance,
        })

    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        instance = getattr(booking, 'manual_payment', None)
        if instance and instance.status == 'approved':
            messages.info(request, 'تمت الموافقة على الدفعة اليدوية بالفعل.')
            return redirect('payments:payment_success')
        form = ManualPaymentForm(request.POST, request.FILES, instance=None)
        if form.is_valid():
            # امنع ازدواجية السجل
            ManualPayment.objects.filter(booking=booking).delete()
            mp = form.save(commit=False)
            mp.booking = booking
            mp.status = 'pending'
            mp.save()
            messages.success(request, 'تم إرسال إثبات الدفع. سيتم مراجعته من قبل الإدارة قريباً.')
            return redirect('payments:manual_payment_status', booking_id=booking.id)
        return render(request, 'payments/manual_payment.html', {
            'booking': booking,
            'form': form,
            'receiver_number': self.VODAFONE_CASH_RECEIVER,
            'instance': instance,
        })


class ManualPaymentStatusView(LoginRequiredMixin, TemplateView):
    template_name = 'payments/manual_payment_status.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking = get_object_or_404(Booking, id=kwargs.get('booking_id'), user=self.request.user)
        manual_payment = getattr(booking, 'manual_payment', None)
        context.update({
            'booking': booking,
            'manual_payment': manual_payment,
        })
        return context
    
    def _handle_payment_success(self, payment_intent):
        """معالجة نجاح الدفع"""
        try:
            payment = Payment.objects.get(
                stripe_payment_intent_id=payment_intent['id']
            )
            payment.status = 'succeeded'
            payment.stripe_charge_id = payment_intent.get('charges', {}).get('data', [{}])[0].get('id', '')
            payment.save()
            
            # تحديث حالة الحجز
            booking = payment.booking
            booking.payment_status = 'paid'
            booking.status = 'confirmed'
            booking.save()
            
        except Payment.DoesNotExist:
            pass
    
    def _handle_payment_failed(self, payment_intent):
        """معالجة فشل الدفع"""
        try:
            payment = Payment.objects.get(
                stripe_payment_intent_id=payment_intent['id']
            )
            payment.status = 'failed'
            payment.failure_reason = payment_intent.get('last_payment_error', {}).get('message', '')
            payment.save()
            
            # تحديث حالة الحجز
            booking = payment.booking
            booking.payment_status = 'failed'
            booking.save()
            
        except Payment.DoesNotExist:
            pass


class PaymentSuccessView(LoginRequiredMixin, TemplateView):
    """صفحة نجاح الدفع"""
    template_name = 'payments/success.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # التحقق من session_id في URL parameters
        session_id = self.request.GET.get('session_id')
        
        if session_id:
            # التحقق من حالة الدفع مباشرة من Stripe
            try:
                session = stripe.checkout.Session.retrieve(session_id)
                booking_id = session.metadata.get('booking_id')
                
                if booking_id and session.payment_status == 'paid':
                    booking = Booking.objects.get(id=booking_id, user=self.request.user)
                    
                    # تحديث حالة الحجز إذا لم يتم تحديثها بعد
                    if booking.payment_status != 'paid':
                        booking.payment_status = 'paid'
                        booking.status = 'confirmed'
                        booking.save()
                        logger.info(f'Booking {booking_id} status updated to paid via success page')
                        
                        # إنشاء سجل الدفع إذا لم يكن موجوداً
                        Payment.objects.get_or_create(
                            booking=booking,
                            defaults={
                                'stripe_payment_intent_id': session.payment_intent,
                                'amount': booking.total_amount,
                                'currency': 'EGP',
                                'status': 'succeeded',
                            }
                        )
                        logger.info(f'Payment record created for booking {booking_id}')
                    
                    context['booking'] = booking
                    context['payment'] = Payment.objects.filter(booking=booking).first()
                    
            except Exception as e:
                print(f'Error retrieving session: {e}')
        
        # البحث عن آخر حجز مدفوع للمستخدم كبديل
        if 'booking' not in context:
            try:
                latest_booking = Booking.objects.filter(
                    user=self.request.user,
                    payment_status='paid'
                ).order_by('-created_at').first()
                
                if latest_booking:
                    context['booking'] = latest_booking
                    context['payment'] = Payment.objects.filter(booking=latest_booking).first()
            except:
                pass
                
        return context


class PaymentCancelView(LoginRequiredMixin, TemplateView):
    """صفحة إلغاء الدفع"""
    template_name = 'payments/cancel.html'


@csrf_exempt
def check_payment_status(request):
    """التحقق من حالة الدفع يدوياً"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    try:
        data = json.loads(request.body)
        booking_id = data.get('booking_id')
        
        booking = get_object_or_404(Booking, id=booking_id)
        
        # البحث عن session في Stripe
        sessions = stripe.checkout.Session.list(
            limit=10,
            expand=['data.payment_intent']
        )
        
        for session in sessions.data:
            if session.metadata.get('booking_id') == str(booking_id):
                if session.payment_status == 'paid':
                    # تحديث حالة الحجز
                    booking.payment_status = 'paid'
                    booking.status = 'confirmed'
                    booking.save()
                    
                    # إنشاء سجل الدفع إذا لم يكن موجوداً
                    Payment.objects.get_or_create(
                        booking=booking,
                        defaults={
                            'stripe_payment_intent_id': session.payment_intent,
                            'amount': booking.total_amount,
                            'currency': 'EGP',
                            'status': 'succeeded',
                        }
                    )
                    
                    return JsonResponse({
                        'status': 'success',
                        'payment_status': 'paid',
                        'message': 'تم تحديث حالة الدفع بنجاح'
                    })
        
        return JsonResponse({
            'status': 'pending',
            'payment_status': booking.payment_status,
            'message': 'لم يتم العثور على دفعة مكتملة'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
