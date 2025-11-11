from django.urls import path
from .views.kuesioner_list_create_view import kuesioner_list_create
from .views.kuesioner_detail_view import kuesioner_detail
from .views.kuesioner_join_view import kuesioner_join, update_guest_name, get_kuesioner_by_pin
from .views.session_recap_view import get_session_recap, get_detailed_session_recap, export_session_data


urlpatterns = [
    path('', kuesioner_list_create, name='kuesioner-list-create'),
    path('<uuid:kuesioner_id>/', kuesioner_detail, name='kuesioner-detail'),

    # Guest join endpoints
    path('<uuid:kuesioner_id>/join/', kuesioner_join, name='kuesioner-join'),
    path('guest-attempts/<uuid:attempt_id>/update-name/', update_guest_name, name='update-guest-name'),
    
    # Public endpoint for PIN
    path('kuesioner-by-pin/<int:pin>/', get_kuesioner_by_pin, name='get-kuesioner-by-pin'),
    
    # Session recap endpoints for Polling and Open Ended
    path('<uuid:kuesioner_id>/session-recap/', get_session_recap, name='session-recap'),
    path('<uuid:kuesioner_id>/session-recap/<uuid:session_id>/', get_detailed_session_recap, name='detailed-session-recap'),
    path('<uuid:kuesioner_id>/export-sessions/', export_session_data, name='export-sessions'),
]