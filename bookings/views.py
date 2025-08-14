from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Message, Booking

@login_required
def user_chats(request):
    user = request.user
    # جلب كل الحجوزات التي فيها رسائل تخص المستخدم
    from django.db.models import Q
    booking_ids = Message.objects.filter(Q(sender=user) | Q(receiver=user)).values_list('booking_id', flat=True).distinct()
    bookings_with_msgs = Booking.objects.filter(id__in=booking_ids)
    chats = []
    for booking in bookings_with_msgs:
        last_msg = booking.messages.order_by('-sent_at').first()
        if last_msg:
            other_user = last_msg.sender if last_msg.sender != user else last_msg.receiver
        else:
            other_user = None
        unread_count = booking.messages.filter(receiver=user, is_read=False).count()
        chats.append({
            'booking': booking,
            'other_user': other_user,
            'unread_count': unread_count,
        })
    return render(request, 'bookings/user_chats.html', {'chats': chats})
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, FormView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from listings.models import Bed
from .models import Booking, Message, BookingOrder
from .forms import BookingForm
import re
import json
from django.http import JsonResponse
from django.conf import settings
import logging
import stripe
logger = logging.getLogger(__name__)
from datetime import date


class MyBookingsView(LoginRequiredMixin, ListView):
    """صفحة حجوزات المستخدم"""
    model = Booking
    template_name = 'bookings/my_bookings.html'
    context_object_name = 'bookings'
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).order_by('-created_at')


class BookBedView(LoginRequiredMixin, FormView):
    """صفحة حجز السرير"""
    template_name = 'bookings/book_bed.html'
    form_class = BookingForm
    
    def dispatch(self, request, *args, **kwargs):
        self.bed = get_object_or_404(Bed, id=kwargs['bed_id'])
        
        # التحقق من توفر السرير
        if not self.bed.is_available:
            messages.error(request, 'هذا السرير غير متاح للحجز.')
            return redirect('listings:apartment_detail', pk=self.bed.room.apartment.id)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bed'] = self.bed
        context['apartment'] = self.bed.room.apartment
        context['room'] = self.bed.room
        return context
    
    def form_valid(self, form):
        # إنشاء الحجز
        booking = form.save(commit=False)
        booking.user = self.request.user
        booking.bed = self.bed
        booking.monthly_price = self.bed.monthly_price
        
        # حساب المبلغ الإجمالي (شهر واحد)
        booking.total_amount = self.bed.monthly_price
        booking.save()
        
        messages.success(self.request, 'تم إنشاء الحجز بنجاح! يرجى إتمام عملية الدفع.')
        return redirect('payments:payment', booking_id=booking.id)
    
    def get_success_url(self):
        return reverse_lazy('bookings:my_bookings')


class CreateMultiBookingView(LoginRequiredMixin, View):
    """إنشاء عدة حجوزات لأسرة متعددة داخل نفس الشقة وبنفس التواريخ، ثم تجهيز الدفع كطلب واحد."""
    def post(self, request):
        try:
            data = json.loads(request.body)
        except Exception:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        try:
            bed_ids = data.get('bed_ids') or []
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            payment_method = (data.get('payment_method') or 'stripe').lower()

            if not isinstance(bed_ids, list) or not bed_ids:
                return JsonResponse({'error': 'يجب تحديد الأسرة'}, status=400)
            if not start_date or not end_date:
                return JsonResponse({'error': 'برجاء تحديد تاريخ البداية والنهاية'}, status=400)

            # Parse dates
            try:
                start_dt = date.fromisoformat(start_date)
                end_dt = date.fromisoformat(end_date)
            except Exception:
                return JsonResponse({'error': 'صيغة التاريخ غير صحيحة. استخدم YYYY-MM-DD'}, status=400)
            if end_dt < start_dt:
                return JsonResponse({'error': 'تاريخ النهاية يجب أن يكون بعد أو يساوي تاريخ البداية'}, status=400)

            beds = list(Bed.objects.filter(id__in=bed_ids))
            if len(beds) != len(bed_ids):
                return JsonResponse({'error': 'بعض الأسرة المحددة غير موجودة'}, status=400)
            # تحقق من توفر كل سرير بدون الاعتماد على اسم حقل محدد
            unavailable = []
            for b in beds:
                is_available = True
                if hasattr(b, 'is_available'):
                    is_available = bool(getattr(b, 'is_available'))
                elif hasattr(b, 'status'):
                    is_available = getattr(b, 'status') == 'available'
                if not is_available:
                    unavailable.append(b.id)
            if unavailable:
                return JsonResponse({'error': 'بعض الأسرة غير متاحة', 'beds': unavailable}, status=400)
            apartment_ids = {b.room.apartment_id for b in beds}
            if len(apartment_ids) != 1:
                return JsonResponse({'error': 'يجب أن تكون كل الأسرة داخل نفس الشقة'}, status=400)

            # إنشاء الحجوزات
            bookings = []
            for bed in beds:
                booking = Booking.objects.create(
                    user=request.user,
                    bed=bed,
                    start_date=start_dt,
                    end_date=end_dt,
                    monthly_price=bed.monthly_price,
                    total_amount=bed.monthly_price,
                )
                bookings.append(booking)
            total_commission = sum(float(getattr(b, 'commission_amount', 150)) for b in bookings)
            order = BookingOrder.objects.create(user=request.user, total_amount=total_commission, status='pending')
            for b in bookings:
                b.order = order
                b.save(update_fields=['order'])

            if payment_method == 'vodafone':
                # وجّه لصفحة الدفع اليدوي الخاصة بالأمر لعرض التعليمات وروابط كل حجز
                from django.urls import reverse
                manual_url = reverse('payments:multi_manual_payment', args=[order.id])
                return JsonResponse({'manual_url': manual_url, 'order_id': order.id})
            else:
                # Stripe
                secret = (settings.STRIPE_SECRET_KEY or '').strip().strip('"').strip("'")
                if not secret or not secret.startswith('sk_'):
                    logger.error("Stripe SECRET key invalid or quoted. Raw value: %r", settings.STRIPE_SECRET_KEY)
                    return JsonResponse({'error': 'Stripe secret key is invalid. تأكد من إزالة علامات الاقتباس من .env وإعادة تشغيل السيرفر.'}, status=500)

                try:
                    stripe.api_key = secret
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

                    success_url = request.build_absolute_uri('/payments/success/') + '?session_id={CHECKOUT_SESSION_ID}'
                    cancel_url = request.build_absolute_uri('/payments/cancel/')
                    session = stripe.checkout.Session.create(
                        payment_method_types=['card'],
                        line_items=line_items,
                        mode='payment',
                        success_url=success_url,
                        cancel_url=cancel_url,
                        metadata={'order_id': order.id},
                    )
                    return JsonResponse({'session_url': session.url})
                except Exception as e:
                    logger.exception("Stripe order checkout session creation failed (order_id=%s)", order.id)
                    return JsonResponse({'error': str(e)}, status=500)
        except Exception as e:
            logger.exception("Unexpected error in CreateMultiBookingView")
            return JsonResponse({'error': 'خطأ غير متوقع: ' + str(e)}, status=500)


@login_required
def chat_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    user = request.user
    # تحقق من أن المستخدم هو صاحب الحجز أو مالك الوحدة
    if not (user == booking.user or user == booking.bed.room.apartment.owner):
        messages.error(request, 'غير مصرح لك بالدخول إلى هذه المحادثة.')
        return redirect('bookings:my_bookings')
    # تحقق من دفع العمولة
    if booking.payment_status != 'paid':
        messages.warning(request, 'يجب دفع العمولة أولاً لفتح الشات.')
        return redirect('bookings:my_bookings')
    # إرسال رسالة جديدة
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        forbidden_patterns = [
            r'\b\d{10,}\b',
            r'\b[\w\.-]+@[\w\.-]+\.\w+\b',
            r'(https?://|www\.)\S+',
        ]
        if any(re.search(pattern, text) for pattern in forbidden_patterns):
            messages.error(request, 'لا يسمح بإرسال بيانات التواصل أو الروابط.')
        elif text:
            Message.objects.create(
                booking=booking,
                sender=user,
                receiver=booking.bed.room.apartment.owner if user == booking.user else booking.user,
                text=text
            )
            # إشعار للطرف الآخر بوجود رسالة جديدة
            # يمكن لاحقاً ربطها بنظام إشعارات أو بريد إلكتروني
            messages.success(request, 'تم إرسال الرسالة بنجاح وسيتم إعلام الطرف الآخر بوجود رسالة جديدة.')
        return redirect('bookings:chat', booking_id=booking.id)
    # عرض الرسائل
    messages_qs = Message.objects.filter(booking=booking).order_by('sent_at')
    # تحديد عدد الرسائل غير المقروءة للطرف الآخر
    unread_count = Message.objects.filter(
        booking=booking,
        receiver=user,
        is_read=False
    ).count()
    # عند فتح الشات، اعتبر جميع الرسائل للطرف الحالي مقروءة
    Message.objects.filter(booking=booking, receiver=user, is_read=False).update(is_read=True)
    return render(request, 'bookings/chat.html', {
        'booking': booking,
        'messages': messages_qs,
        'user': user,
        'unread_count': unread_count,
    })
