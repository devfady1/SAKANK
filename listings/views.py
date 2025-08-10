from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, FormView, TemplateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import inlineformset_factory
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Apartment, Location, Room, Bed
from .forms import ApartmentForm, RoomForm, RoomUpdateForm, BedForm, RoomWithPriceForm


class ApartmentListView(ListView):
    """صفحة قائمة الشقق"""
    model = Apartment
    template_name = 'listings/apartment_list.html'
    context_object_name = 'apartments'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Apartment.objects.filter(is_active=True)
        
        # البحث
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(location__name__icontains=search)
            )
        
        # فلترة حسب الموقع
        location_id = self.request.GET.get('location')
        if location_id:
            queryset = queryset.filter(location_id=location_id)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['locations'] = Location.objects.filter(is_active=True)
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_location'] = self.request.GET.get('location', '')
        return context


class ApartmentDetailView(DetailView):
    """صفحة تفاصيل الشقة"""
    model = Apartment
    template_name = 'listings/apartment_detail.html'
    context_object_name = 'apartment'
    
    def get_queryset(self):
        return Apartment.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        apartment = self.get_object()
        context['rooms'] = apartment.rooms.all()
        # إظهار بيانات التواصل فقط إذا كان الطالب دفع العربون أو العمولة
        show_contact = False
        user = self.request.user
        if user.is_authenticated and user.user_type == 'buyer':
            from bookings.models import Booking
            # تحقق من وجود حجز مدفوع لهذا الطالب على سرير في هذه الشقة
            paid_booking = Booking.objects.filter(
                user=user,
                bed__room__apartment=apartment,
                payment_status='paid'
            ).exists()
            if paid_booking:
                show_contact = True
        context['show_contact'] = show_contact
        return context


class SellerDashboardView(LoginRequiredMixin, TemplateView):
    """لوحة تحكم البائع"""
    template_name = 'listings/seller_dashboard.html'
    
    def dispatch(self, request, *args, **kwargs):
        # LoginRequiredMixin سيتولى التحقق من تسجيل الدخول
        response = super().dispatch(request, *args, **kwargs)
        
        # التحقق من نوع المستخدم بعد التأكد من تسجيل الدخول
        if hasattr(request.user, 'user_type') and request.user.user_type != 'seller':
            messages.error(request, 'هذه الصفحة مخصصة للبائعين فقط.')
            return redirect('pages:index')
        
        return response
    
    def get_context_data(self, **kwargs):
        from bookings.models import Booking
        from django.db.models import Count
        
        context = super().get_context_data(**kwargs)
        apartments = Apartment.objects.filter(owner=self.request.user)
        context['apartments'] = apartments
        
        # إحصائيات سريعة
        context['total_apartments'] = apartments.count()
        context['total_rooms'] = sum(apartment.rooms.count() for apartment in apartments)
        context['total_beds'] = sum(
            sum(room.beds.count() for room in apartment.rooms.all()) 
            for apartment in apartments
        )
        
        # إحصائيات الحجوزات
        all_beds = []
        for apartment in apartments:
            for room in apartment.rooms.all():
                all_beds.extend(room.beds.all())
        
        context['total_bookings'] = Booking.objects.filter(bed__in=all_beds).count()
        context['recent_bookings'] = Booking.objects.filter(
            bed__in=all_beds
        ).order_by('-created_at')[:5]
        
        return context


class AddApartmentView(LoginRequiredMixin, FormView):
    """إضافة شقة جديدة"""
    template_name = 'listings/add_apartment.html'
    form_class = ApartmentForm
    success_url = reverse_lazy('listings:seller_dashboard')
    
    def dispatch(self, request, *args, **kwargs):
        # LoginRequiredMixin سيتولى التحقق من تسجيل الدخول
        response = super().dispatch(request, *args, **kwargs)
        
        # التحقق من نوع المستخدم بعد التأكد من تسجيل الدخول
        if hasattr(request.user, 'user_type') and request.user.user_type != 'seller':
            messages.error(request, 'هذه الصفحة مخصصة للبائعين فقط.')
            return redirect('pages:index')
        
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        RoomFormSet = inlineformset_factory(
            Apartment,
            Room,
            form=RoomWithPriceForm,
            fields=['name', 'bed_count', 'room_image', 'description'],
            extra=1,
            can_delete=True
        )
        if self.request.method == 'POST':
            # عرض مؤقت بدون instance (سيُعاد توليده في POST الفعلي بعد حفظ الشقة)
            context['room_formset'] = RoomFormSet(prefix='room_set')
        else:
            context['room_formset'] = RoomFormSet(instance=Apartment(), prefix='room_set')
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        RoomFormSet = inlineformset_factory(
            Apartment,
            Room,
            form=RoomWithPriceForm,
            fields=['name', 'bed_count', 'room_image', 'description'],
            extra=1,
            can_delete=True
        )
        if form.is_valid():
            # احفظ الشقة أولاً
            apartment = form.save(commit=False)
            apartment.owner = request.user
            apartment.save()

            # اربط formset بالـ instance المحفوظ
            formset = RoomFormSet(request.POST, request.FILES, instance=apartment, prefix='room_set')
            if formset.is_valid():
                # لا نستخدم formset.save() مباشرة لأننا نحتاج bed_price
                for room_form in formset.forms:
                    if not room_form.cleaned_data or room_form.cleaned_data.get('DELETE'):
                        continue
                    room = room_form.save(commit=False)
                    room.apartment = apartment
                    room.save()
                    # إنشاء الأسرة حسب العدد وبالسعر المحدد
                    bed_count = room_form.cleaned_data.get('bed_count') or 0
                    bed_price = room_form.cleaned_data.get('bed_price') or 0
                    for i in range(1, int(bed_count) + 1):
                        Bed.objects.create(
                            room=room,
                            bed_number=str(i),
                            monthly_price=bed_price
                        )

                # حذف العناصر المعلمة بالحذف (إن وجدت) بشكل يدوي
                for room_form in formset.forms:
                    if room_form.cleaned_data.get('DELETE') and getattr(room_form.instance, 'pk', None):
                        room_form.instance.delete()

                messages.success(request, 'تم إضافة الشقة والغرف بنجاح!')
                return redirect(self.get_success_url())

            # إن فشل formset: أعِد عرض الصفحة مع الأخطاء
            context = self.get_context_data()
            context['form'] = form
            context['room_formset'] = formset
            return self.render_to_response(context)

        # إن فشل form الأساسي
        return self.form_invalid(form)


class AddRoomView(LoginRequiredMixin, FormView):
    """إضافة غرفة جديدة"""
    template_name = 'listings/add_room.html'
    form_class = RoomForm
    
    def dispatch(self, request, *args, **kwargs):
        # التحقق من نوع المستخدم بعد التأكد من تسجيل الدخول
        if hasattr(request.user, 'user_type') and request.user.user_type != 'seller':
            messages.error(request, 'هذه الصفحة مخصصة للبائعين فقط.')
            return redirect('pages:index')

        # التحقق من ملكية الشقة يجب أن يتم قبل متابعة المعالجة حتى يتاح استخدامها في get_context_data
        self.apartment = get_object_or_404(
            Apartment,
            id=kwargs['apartment_id'],
            owner=request.user
        )

        # LoginRequiredMixin سيتولى التحقق من تسجيل الدخول
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['apartment'] = self.apartment
        return context
    
    def form_valid(self, form):
        room = form.save(commit=False)
        room.apartment = self.apartment
        room.save()
        
        # إنشاء الأسرة للغرفة
        bed_count = form.cleaned_data['bed_count']
        for i in range(1, bed_count + 1):
            Bed.objects.create(
                room=room,
                bed_number=str(i),
                monthly_price=form.cleaned_data['bed_price']
            )
        
        messages.success(self.request, f'تم إضافة الغرفة مع {bed_count} أسرة بنجاح!')
        return redirect('listings:seller_dashboard')
    
    def get_success_url(self):
        return reverse_lazy('listings:seller_dashboard')


class ApartmentUpdateView(LoginRequiredMixin, UpdateView):
    """تعديل شقة"""
    model = Apartment
    template_name = 'listings/edit_apartment.html'
    form_class = ApartmentForm
    success_url = reverse_lazy('listings:seller_dashboard')

    def get_queryset(self):
        # السماح بتعديل شقق المالك فقط
        return Apartment.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'تم تعديل الشقة بنجاح!')
        return super().form_valid(form)


class ApartmentDeleteView(LoginRequiredMixin, DeleteView):
    """حذف شقة"""
    model = Apartment
    template_name = 'listings/confirm_delete.html'
    success_url = reverse_lazy('listings:seller_dashboard')

    def get_queryset(self):
        return Apartment.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'حذف الشقة'
        context['cancel_url'] = reverse_lazy('listings:seller_dashboard')
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'تم حذف الشقة بنجاح!')
        return super().delete(request, *args, **kwargs)


class RoomUpdateView(LoginRequiredMixin, UpdateView):
    """تعديل غرفة"""
    model = Room
    template_name = 'listings/edit_room.html'
    form_class = RoomUpdateForm
    success_url = reverse_lazy('listings:seller_dashboard')

    def get_queryset(self):
        # الغرف التابعة لشقق المالك فقط
        return Room.objects.filter(apartment__owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'تم تعديل الغرفة بنجاح!')
        return super().form_valid(form)


class RoomDeleteView(LoginRequiredMixin, DeleteView):
    """حذف غرفة"""
    model = Room
    template_name = 'listings/confirm_delete.html'
    success_url = reverse_lazy('listings:seller_dashboard')

    def get_queryset(self):
        return Room.objects.filter(apartment__owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'حذف الغرفة'
        context['cancel_url'] = reverse_lazy('listings:seller_dashboard')
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'تم حذف الغرفة بنجاح!')
        return super().delete(request, *args, **kwargs)


class BedUpdateView(LoginRequiredMixin, UpdateView):
    """تعديل سرير"""
    model = Bed
    template_name = 'listings/edit_bed.html'
    form_class = BedForm
    success_url = reverse_lazy('listings:seller_dashboard')

    def get_queryset(self):
        # الأسرة التابعة لشقق المالك فقط
        return Bed.objects.filter(room__apartment__owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'تم تعديل السرير بنجاح!')
        return super().form_valid(form)


class BedDeleteView(LoginRequiredMixin, DeleteView):
    """حذف سرير"""
    model = Bed
    template_name = 'listings/confirm_delete.html'
    success_url = reverse_lazy('listings:seller_dashboard')

    def get_queryset(self):
        return Bed.objects.filter(room__apartment__owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'حذف السرير'
        context['cancel_url'] = reverse_lazy('listings:seller_dashboard')
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'تم حذف السرير بنجاح!')
        return super().delete(request, *args, **kwargs)
