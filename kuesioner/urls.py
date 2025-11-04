from django.urls import path
from .views.kuesioner_list_create_view import kuesioner_list_create
from .views.kuesioner_detail_view import kuesioner_detail
from .views.kuesioner_join_view import kuesioner_join, update_guest_name, get_kuesioner_by_pin


urlpatterns = [
    path('', kuesioner_list_create, name='kuesioner-list-create'),
    path('<uuid:kuesioner_id>/', kuesioner_detail, name='kuesioner-detail'),

    # Guest join endpoints
    path('<uuid:kuesioner_id>/join/', kuesioner_join, name='kuesioner-join'),
    path('guest-attempts/<uuid:attempt_id>/update-name/', update_guest_name, name='update-guest-name'),
    
    # Public endpoint for PIN
    path('kuesioner-by-pin/<int:pin>/', get_kuesioner_by_pin, name='get-kuesioner-by-pin'),
]