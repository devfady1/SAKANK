from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('my-bookings/', views.MyBookingsView.as_view(), name='my_bookings'),
    path('book/<int:bed_id>/', views.BookBedView.as_view(), name='book_bed'),
    path('chat/<int:booking_id>/', views.chat_view, name='chat'),
        path('user-chats/', views.user_chats, name='user_chats'),
    ]
