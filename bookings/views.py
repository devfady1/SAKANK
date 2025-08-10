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
from django.views.generic import ListView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from listings.models import Bed
from .models import Booking, Message
from .forms import BookingForm
import re


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
