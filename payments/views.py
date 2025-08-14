import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from bookings.models import Booking, BookingOrder

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
    # نستخدم عمولة المنصة فقط
    if not hasattr(booking, 'commission_amount') or booking.commission_amount is None or booking.commission_amount <= 0:
        return JsonResponse({'error': 'قيمة العمولة غير صالحة'}, status=400)

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
                        'name': f'عمولة المنصة لحجز سرير #{booking.bed_id}',
                    },
                    'unit_amount': int(float(booking.commission_amount) * 100),
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


@csrf_exempt
def create_order_checkout_session(request):
    """إنشاء جلسة دفع Stripe لعدة حجوزات في أمر واحد."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    import json
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    ids = data.get('booking_ids') or []
    if not isinstance(ids, list) or not ids:
        return JsonResponse({'error': 'booking_ids required'}, status=400)

    # اجلب الحجوزات وتأكد أنها للمستخدم الحالي
    bookings = list(Booking.objects.filter(id__in=ids))
    if not bookings:
        return JsonResponse({'error': 'لا توجد حجوزات'}, status=404)
    user = bookings[0].user
    # تأكد أن جميع الحجوزات لنفس المستخدم
    if any(b.user_id != user.id for b in bookings):
        return JsonResponse({'error': 'جميع الحجوزات يجب أن تخص نفس المستخدم'}, status=400)

    # احسب إجمالي العمولات فقط
    try:
        total = sum([float(getattr(b, 'commission_amount', 150)) for b in bookings])
    except Exception:
        return JsonResponse({'error': 'مبالغ غير صحيحة'}, status=400)
    if total <= 0:
        return JsonResponse({'error': 'إجمالي غير صالح'}, status=400)

    # أنشئ أمر الحجز
    order = BookingOrder.objects.create(user=user, total_amount=total, status='pending')
    for b in bookings:
        b.order = order
        b.save(update_fields=['order'])

    # تهيئة Stripe
    import logging
    logger = logging.getLogger('payments')
    secret = (settings.STRIPE_SECRET_KEY or '').strip().strip('"').strip("'")
    if not secret or not secret.startswith('sk_'):
        logger.error("Stripe SECRET key invalid or quoted. Raw value: %r", settings.STRIPE_SECRET_KEY)
        return JsonResponse({'error': 'Stripe secret key is invalid. تأكد من إزالة علامات الاقتباس من .env وأعد تشغيل السيرفر.'}, status=500)
    try:
        stripe.api_key = secret
        # ضع كل حجز كبند مستقل لشفافية الفاتورة
        line_items = []
        for b in bookings:
            line_items.append({
                'price_data': {
                    'currency': 'egp',
                    'product_data': {
                        'name': f'عمولة المنصة لحجز سرير #{b.bed_id}',
                    },
                    'unit_amount': int(float(getattr(b, 'commission_amount', 150)) * 100),
                },
                'quantity': 1,
            })
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=request.build_absolute_uri('/payments/success/') + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri('/payments/cancel/'),
            metadata={'order_id': order.id},
        )
        return JsonResponse({'session_url': session.url})
    except Exception as e:
        logger.exception("Stripe order checkout session creation failed (order_id=%s)", order.id)
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


class MultiManualPaymentView(LoginRequiredMixin, TemplateView):
    """عرض صفحة الدفع اليدوي لحجز متعدد (أمر حجوزات)."""
    template_name = 'payments/manual_order.html'

    def get_context_data(self, **kwargs):
        from bookings.models import BookingOrder
        context = super().get_context_data(**kwargs)
        order_id = kwargs.get('order_id')
        order = get_object_or_404(BookingOrder, id=order_id, user=self.request.user)
        bookings = list(order.bookings.all())
        total_commission = sum(float(getattr(b, 'commission_amount', 150)) for b in bookings)
        context.update({
            'order': order,
            'bookings': bookings,
            'total_commission': total_commission,
            'warning': 'تنبيه هام: الدفع هنا هو عمولة المنصة فقط (150 جنيه لكل سرير). هذا ليس سعر السرير.',
            'receiver_number': ManualPaymentView.VODAFONE_CASH_RECEIVER,
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

    VODAFONE_CASH_RECEIVER = "01551954315"

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
            # خزّن وقت التحويل في ملاحظات المشرف بدون تعديل الموديل
            transfer_time = form.cleaned_data.get('transfer_time')
            notes_parts = []
            if transfer_time:
                notes_parts.append(f"وقت التحويل: {transfer_time}")
            if mp.transaction_ref:
                notes_parts.append(f"رقم العملية: {mp.transaction_ref}")
            if mp.sender_phone:
                notes_parts.append(f"هاتف المُرسل: {mp.sender_phone}")
            if notes_parts:
                mp.admin_notes = (mp.admin_notes + "\n" if mp.admin_notes else "") + " | ".join(notes_parts)
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
            try:
                secret = (settings.STRIPE_SECRET_KEY or '').strip().strip('"').strip("'")
                stripe.api_key = secret
                session = stripe.checkout.Session.retrieve(session_id)
                order_id = session.metadata.get('order_id')
                booking_id = session.metadata.get('booking_id')
                if order_id:
                    # معالجة أمر متعدد الحجوزات
                    order = get_object_or_404(BookingOrder, id=order_id, user=self.request.user)
                    if session.payment_status == 'paid' and order.status != 'paid':
                        order.status = 'paid'
                        order.save(update_fields=['status'])
                        for b in order.bookings.all():
                            b.payment_status = 'paid'
                            b.status = 'confirmed'
                            b.save(update_fields=['payment_status', 'status'])
                            Payment.objects.get_or_create(
                                booking=b,
                                defaults={
                                    'stripe_payment_intent_id': session.payment_intent,
                                    'amount': b.commission_amount,
                                    'currency': 'EGP',
                                    'status': 'succeeded',
                                }
                            )
                        context['order'] = order
                        context['bookings'] = list(order.bookings.all())
                elif booking_id:
                    booking = get_object_or_404(Booking, id=booking_id, user=self.request.user)
                    if session.payment_status == 'paid':
                        booking.payment_status = 'paid'
                        booking.status = 'confirmed'
                        booking.save()
                        logger.info(f'Booking {booking_id} status updated to paid via success page')
                        
                        # إنشاء سجل الدفع إذا لم يكن موجوداً
                        Payment.objects.get_or_create(
                            booking=booking,
                            defaults={
                                'stripe_payment_intent_id': session.payment_intent,
                                'amount': booking.commission_amount,
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
