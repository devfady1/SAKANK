from django.urls import path
from . import views

app_name = 'listings'

urlpatterns = [
    path('', views.ApartmentListView.as_view(), name='apartment_list'),
    path('apartment/<int:pk>/', views.ApartmentDetailView.as_view(), name='apartment_detail'),
    path('seller/dashboard/', views.SellerDashboardView.as_view(), name='seller_dashboard'),
    path('seller/add-apartment/', views.AddApartmentView.as_view(), name='add_apartment'),
    path('seller/add-room/<int:apartment_id>/', views.AddRoomView.as_view(), name='add_room'),
    # CRUD: Apartment
    path('seller/apartment/<int:pk>/edit/', views.ApartmentUpdateView.as_view(), name='edit_apartment'),
    path('seller/apartment/<int:pk>/delete/', views.ApartmentDeleteView.as_view(), name='delete_apartment'),
    # CRUD: Room
    path('seller/room/<int:pk>/edit/', views.RoomUpdateView.as_view(), name='edit_room'),
    path('seller/room/<int:pk>/delete/', views.RoomDeleteView.as_view(), name='delete_room'),
    # CRUD: Bed
    path('seller/bed/<int:pk>/edit/', views.BedUpdateView.as_view(), name='edit_bed'),
    path('seller/bed/<int:pk>/delete/', views.BedDeleteView.as_view(), name='delete_bed'),
]
