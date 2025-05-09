from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('likes/', views.my_likes, name='likes'),
    path('search/', views.search, name='search'),
    path('create_post/', views.create_post_page, name='create_post' ),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('comment/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('repost/<int:post_id>/', views.repost, name='repost'),
    path('post/delete/<int:post_id>/', views.delete_post, name='delete_post'),
]