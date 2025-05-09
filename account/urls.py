from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login/',views.login,name='login'),
    path('register/',views.register,name="register"),
    path('profile/',views.profile,name="profile"),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow_user'),
    path('create_post/', views.create_post, name='create_post'),
    path('profile/<int:user_id>/', views.views_profile, name='user_profile'),
    path('profile/<int:user_id>/', views.views_profile, name='user_profile'),
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow_user'),
    path('logout/', views.logout, name='logout'),
    path('like_post/<int:post_id>/', views.like_post, name='like_post'),
    path('chats/', views.chat_list_view, name='chat_list'),
    path('chat/<int:chat_id>/', views.chat_detail, name='chat_detail'),
    path('chat/<int:user_id>', views.open_chat, name='open_chat'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)