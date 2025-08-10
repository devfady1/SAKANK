#!/usr/bin/env python
"""
ملف لإنشاء بيانات تجريبية لمشروع سكنك
"""
import os
import sys
import django

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sakanak.settings')
django.setup()

from accounts.models import User
from listings.models import Location, Apartment, Room, Bed

def create_sample_data():
    """إنشاء بيانات تجريبية لأسيوط الجديدة"""
    # حذف كل البيانات القديمة
    Location.objects.all().delete()
    Apartment.objects.all().delete()
    Room.objects.all().delete()
    Bed.objects.all().delete()
    User.objects.filter(username__in=['seller_asyut', 'buyer_asyut']).delete()

    # إنشاء موقع واحد فقط
    location, _ = Location.objects.get_or_create(name='أسيوط الجديدة - الحي الأول', city='أسيوط الجديدة')

    # إنشاء بائع مصري
    seller, created = User.objects.get_or_create(
        username='seller_asyut',
        defaults={
            'email': 'sellerasyut@example.com',
            'user_type': 'seller',
            'is_verified': True,
            'phone': '01012345678'
        }
    )
    if created:
        seller.set_password('egypt123')
        seller.save()

    # إنشاء طالب مصري
    buyer, created = User.objects.get_or_create(
        username='buyer_asyut',
        defaults={
            'email': 'buyerasyut@example.com',
            'user_type': 'buyer',
            'phone': '01087654321'
        }
    )
    if created:
        buyer.set_password('egypt123')
        buyer.save()

    # إنشاء شقق وغرف وأسرة
    for i in range(1, 4):
        apt = Apartment.objects.create(
            name=f'شقة عائلية رقم {i} - أسيوط الجديدة',
            location=location,
            owner=seller,
            description=f'شقة واسعة في الحي الأول بأسيوط الجديدة، قريبة من الجامعة، رقم {i}',
            main_image='',
            is_active=True
        )
        for j in range(1, 3):
            room = Room.objects.create(
                apartment=apt,
                name=f'غرفة رقم {j}',
                description=f'غرفة مريحة رقم {j} في الشقة رقم {i}',
                bed_count=2
            )
            for k in range(1, 3):
                Bed.objects.create(
                    room=room,
                    bed_number=k,
                    monthly_price=700 + 50 * k,
                    status='available'
                )
    print('تم إنشاء بيانات أسيوط الجديدة بالكامل!')
    print('بيانات الدخول:')
    print('بائع: seller_asyut / egypt123')
    print('طالب: buyer_asyut / egypt123')

if __name__ == '__main__':
    create_sample_data()
