from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from account.models import CustomUser, Post, Hashtag, Comment
from django.http import HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.http import JsonResponse
from .forms import PostForm


@login_required
def my_likes(request):
    liked_posts = request.user.liked_posts.all()

    return render(request, 'likes.html', {
        'liked_posts': liked_posts,
    })

@login_required
def search(request):
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'posts')

    users = []
    posts = []

    if query:
        if search_type == 'posts':
            posts = Post.objects.filter(
                Q(title__icontains =query) |
                Q(content__icontains=query) |
                Q(hashtags__name__icontains=query)
            ).distinct()
            
        else:
            users = CustomUser.objects.filter(
                Q(username__icontains=query) |
                Q(user_nickname__icontains=query)
            )
    print('Query:', query)
    print('Search Type:', search_type)
    
    return render(request, 'search.html', {
        'query': query,
        'search_type': search_type,
        'users': users,
        'posts': posts,
    })

@login_required
def create_post_page(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            print(form.errors.as_data()) 
            # Хэштеги:
            hashtags_str = form.cleaned_data.get('hashtags', '')
            hashtags_list = [tag.strip().lstrip('#') for tag in hashtags_str.split() if tag.strip()]
            for tag_name in hashtags_list:
                hashtag, _ = Hashtag.objects.get_or_create(name=tag_name)
                post.hashtags.add(hashtag)

            return redirect('profile')  # или 'index' по желанию
        else:
            print("❌ Ошибка формы:", form.errors)
            # показать форму с ошибками на user_profile.html
            posts = Post.objects.filter(user=request.user).order_by('-created_at')
            return render(request, 'user_profile.html', {
                'form': form,
                'posts': posts,
                'active_tab': 'posts',
                'open_modal': True  # <--- флаг, чтобы в шаблоне открыть модалку
            })

    else:
        form = PostForm()
        return render(request, 'create_post.html', {
            'form': form,
        })


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()

    if request.method == 'POST':
        text = request.POST.get('comment')
        if text:
            Comment.objects.create(post=post, user=request.user, text=text)
            return redirect('post_detail', post_id=post.id)

    return render(request, 'post.html', {'post': post, 'comments': comments})

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.user != request.user:
        return HttpResponseForbidden("Вы не можете удалить этот комментарий.")

    comment.delete()

    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.user != request.user:
        return HttpResponseForbidden("Вы не можете удалить этот пост.")

    post.delete()

    return redirect(request.META.get('HTTP_REFERER', '/'))

def repost(request, post_id):
    if not request.user.is_authenticated:
        return redirect('login')

    post = get_object_or_404(Post, id=post_id)

    if post in request.user.reposts.all():
        request.user.reposts.remove(post)  # снять репост
    else:
        request.user.reposts.add(post) # добавить репост
        
    return redirect(request.META.get('HTTP_REFERER', '/')) # или куда надо