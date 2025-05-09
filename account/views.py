from django.shortcuts import render, redirect, get_object_or_404
from .forms import LoginForm, RegisterForm, ProfileEditForm
from django.contrib.auth import authenticate, login as auth_login, get_user_model, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser, Post, Hashtag, Chat, Message
from django.http import JsonResponse
from django.db.models import Q
from django.db.models import Count


@login_required
def profile(request):
    user = request.user
    tab = request.GET.get('type', 'posts') 

    if tab == 'reposts':
        posts = user.reposts.all().order_by('-created_at')
    else:
        posts = Post.objects.filter(user=user).order_by('-created_at')

    return render(request, 'user_profile.html', {
        'user': user,
        'posts': posts,
        'active_tab': tab,
    })


@login_required
def create_post(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        image = request.FILES.get('image')
        hashtags = request.POST.get('hashtags', '') 

        # Создаём новый пост
        post = Post.objects.create(
            user=request.user,
            content=content,
            image=image
        )

        if hashtags:
            hashtags_list = hashtags.split() 
            for hashtag in hashtags_list:
                hashtag_obj, created = Hashtag.objects.get_or_create(name=hashtag)  
                post.hashtags.add(hashtag_obj) 
        return redirect('profile')  

    return redirect('profile') 


@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=user)
    
    return render(request, 'edit_user_profile.html', {'form': form})
def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)  # используем метод auth_login
                return redirect('profile')  # перенаправление после входа
            else:
                form.add_error(None, 'Неверное имя пользователя или пароль')
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        print("Форма получена:", form)  # Печать формы для отладки

        if form.is_valid():
            print("Форма прошла валидацию.")  # Печать при успешной валидации

            # Создание нового пользователя
            user = get_user_model()()
            user.username = form.cleaned_data["username"]
            user.email = form.cleaned_data["email"]
            user.user_nickname = form.cleaned_data["user_nickname"]
            user.age = form.cleaned_data["age"]
            user.set_password(form.cleaned_data["password"])  # Хешируем пароль
            print(f"Данные пользователя: {user.username}, {user.email}, {user.user_nickname}, {user.age}")

            user.save()  # Сохраняем пользователя
            print("Пользователь сохранён.")

            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('login')  # Перенаправление на страницу входа после регистрации
        else:
            print("Форма не прошла валидацию. Ошибки:", form.errors)  # Печать ошибок формы
            messages.error(request, 'Ошибка при регистрации. Проверьте введенные данные.')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})

@login_required
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(CustomUser, id=user_id)
    request.user.followings.add(user_to_follow)  # добавляем в followings
    return redirect('user_profile', user_id=user_id)

@login_required
def unfollow_user(request, user_id):
    user_to_unfollow = get_object_or_404(CustomUser, id=user_id)
    request.user.followings.remove(user_to_unfollow)
    return redirect('user_profile', user_id=user_id)




@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.user == request.user:
        return JsonResponse({'error': 'Вы не можете лайкать свой пост'}, status=400)

    user = request.user
    if user in post.likes.all():
        post.likes.remove(user)
        liked = False
    else:
        post.likes.add(user)
        liked = True

    return JsonResponse({'likes_count': post.likes.count(), 'liked': liked})


def views_profile(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    tab_type = request.GET.get('type', 'posts')  

    if tab_type == 'reposts':
        posts = user.reposts.all().order_by('-created_at')  
    else:
        posts = Post.objects.filter(user=user).order_by('-created_at')

    is_following = request.user.followings.filter(id=user_id).exists()

    return render(request, 'view_profile.html', context={
        'user': user,
        'posts': posts,
        'is_following': is_following,
        'active_tab': tab_type,  
    })



def logout(request):
    auth_logout(request)
    return redirect('login')  

@login_required
def chat_list_view(request, chat_id=None):
    # 1) список чатов, где я — sender или receiver
    user_chats = Chat.objects.filter(
        Q(sender=request.user) |
        Q(receiver=request.user)
    ).order_by('-created_at')

    selected_chat = None
    if chat_id is not None:
        # убедимся, что чат с таким id и я в нём участвую
        selected_chat = get_object_or_404(
            Chat.objects.filter(
                Q(sender=request.user) |
                Q(receiver=request.user),
                id=chat_id
            )
        )

    return render(request, 'messenger.html', {
        'chats':        user_chats,
        'selected_chat': selected_chat,
    })

@login_required
def open_chat(request, user_id):
    # Получаем пользователя, с которым хотим начать чат
    other_user = get_object_or_404(CustomUser, id=user_id)
    
    # Проверяем, существует ли уже чат между текущим пользователем и выбранным пользователем
    chat = Chat.objects.filter(
        Q(sender=request.user, receiver=other_user) | Q(sender=other_user, receiver=request.user)
    ).first()

    if not chat:
        # Если чат не существует, создаём новый
        chat = Chat.objects.create(sender=request.user, receiver=other_user)

    # Переходим на страницу этого чата
    return redirect('chat_detail', chat_id=chat.id)

@login_required
def chat_detail(request, chat_id):
    # Получаем чат по id
    chat = get_object_or_404(Chat, id=chat_id)

    # Проверка, что пользователь участвует в чате
    if request.user != chat.sender and request.user != chat.receiver:
        return redirect('chat_list')  # или 403 Forbidden

    # Отправка сообщения
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(
                chat=chat,
                sender=request.user,
                content=content
            )
            return redirect('chat_detail', chat_id=chat.id)

    return render(request, 'messenger.html', {
        'selected_chat': chat,
        'chats': Chat.objects.filter(Q(sender=request.user) | Q(receiver=request.user)),
    })