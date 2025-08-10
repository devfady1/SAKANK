from django.shortcuts import render, redirect
from django.views.generic import TemplateView, FormView
from django.contrib import messages
from django.db.models import Q
from listings.models import Apartment, Location
from .models import ContactMessage
from .forms import ContactForm


class IndexView(TemplateView):
    """صفحة الرئيسية"""
    template_name = 'pages/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # البحث في الشقق
        search_query = self.request.GET.get('search', '')
        location_id = self.request.GET.get('location', '')
        
        apartments = Apartment.objects.filter(is_active=True)
        
        if search_query:
            apartments = apartments.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(location__name__icontains=search_query)
            )
        
        if location_id:
            apartments = apartments.filter(location_id=location_id)
        
        context.update({
            'apartments': apartments[:8],  # أول 8 شقق
            'locations': Location.objects.filter(is_active=True),
            'search_query': search_query,
            'selected_location': location_id,
        })
        
        return context


class ContactView(FormView):
    """صفحة التواصل"""
    template_name = 'pages/contact.html'
    form_class = ContactForm
    success_url = '/contact/'
    
    def form_valid(self, form):
        # حفظ رسالة التواصل
        ContactMessage.objects.create(
            name=form.cleaned_data['name'],
            email=form.cleaned_data['email'],
            phone=form.cleaned_data.get('phone', ''),
            subject=form.cleaned_data['subject'],
            message=form.cleaned_data['message']
        )
        
        messages.success(self.request, 'تم إرسال رسالتك بنجاح. سنتواصل معك قريباً.')
        return super().form_valid(form)
