from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.crypto import get_random_string

def generate_unique_nickname():
    return 'user_' + get_random_string(8)

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):

        if not email:
            raise ValueError('The Email field must be set ')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, email, password, **extra_fields)




class Post(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='posts',null=True)
    content = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    likes = models.ManyToManyField('CustomUser', related_name='liked_posts', blank=True)
    hashtags = models.ManyToManyField('Hashtag', related_name='posts', blank=True)  # Добавляем связь с хэштегами
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or "" 


from django.conf import settings

class Comment(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Комментарий от {self.user} к посту {self.post.id}'

class Hashtag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name or "" 


class CustomUser(AbstractUser):
    username = models.CharField(max_length=20, unique=True)
    user_nickname = models.CharField(
        max_length=30,
        unique=True,
        default=generate_unique_nickname
    )
    email = models.EmailField(unique=True, blank=True, null=True)
    password = models.CharField(max_length=128)
    first_name = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    description = models.TextField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='followings', blank=True)
    reposts = models.ManyToManyField('Post', related_name='reposted_by', blank=True)


    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    REQUIRED_FIELDS = ['email', 'first_name']
    USERNAME_FIELD = 'username'

    objects = CustomUserManager()

    def __str__(self):
        return self.username

    @property
    def followers_count(self):
        return self.followers.count()
    
    @property
    def following_count(self):
        return self.followings.count()




class Chat(models.Model):
    sender   = models.ForeignKey(settings.AUTH_USER_MODEL,
                                 related_name='sent_chats',
                                 on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL,
                                 related_name='received_chats',
                                 on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('sender', 'receiver')

    def __str__(self):
        return f"Чат {self.sender.username} ↔ {self.receiver.username}"



class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE,related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Сообщение от {self.sender.username} в {self.timestamp}"
