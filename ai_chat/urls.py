from django.urls import path
from . import views

urlpatterns = [
    path('sidebar/', views.chat_sidebar, name='chat_sidebar'),
    path('sidebar/<int:session_id>/', views.chat_sidebar, name='chat_sidebar_detail'),
    path('session/', views.chat_session, name='chat_session'),
    path('session/<int:session_id>/', views.chat_session, name='chat_session_detail'),
    path('session/<int:session_id>/update-title/', views.update_title, name='update_title'),
    path('send-message/', views.send_message, name='send_message'),
    path('delete-session/<int:session_id>/', views.delete_session, name='delete_session'),
    path('delete-all-sessions/', views.delete_all_sessions, name='delete_all_sessions'),
]
