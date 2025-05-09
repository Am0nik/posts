from django.contrib import admin
from .models import CustomUser, Post,Hashtag, Comment, Chat, Message
# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'get_followers_count', 'get_following_count')
    search_fields = ('username', 'email')
    list_filter = ('is_active', 'is_staff')
    ordering = ('id',)
    list_per_page = 20

    # Методы для отображения количества подписчиков и подписок
    def get_followers_count(self, obj):
        return obj.followers_count
    get_followers_count.short_description = 'Подписчиков'

    def get_following_count(self, obj):
        return obj.following_count
    get_following_count.short_description = 'Подписок'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user','display_hashtags', 'created_at')
    search_fields = ('title', 'content')
    list_filter = ('created_at', 'hashtags')
    ordering = ('-created_at',)
    list_per_page = 20
    
    def display_hashtags(self, obj):
        return ", ".join([h.name for h in obj.hashtags.all()])
    display_hashtags.short_description = "хэштеги"

    raw_id_fields = ('user',)
    autocomplete_fields = ('user',)

    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'user', 'hashtags','image','likes')
        }),
    )


@admin.register(Hashtag)
class HeshtagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)
    list_per_page = 50


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'user', 'text', 'created_at')
    search_fields = ('post__title', 'user__username', 'text')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    list_per_page = 20


admin.site.register(Chat)
admin.site.register(Message)