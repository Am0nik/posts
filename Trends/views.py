from django.shortcuts import render
from account.models import Post

def index(request):
    posts = Post.objects.all().order_by('-created_at')  # Получаем все посты, отсортированные по дате
    return render(request, 'index.html', {'posts': posts})