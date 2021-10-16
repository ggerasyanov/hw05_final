from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from yatube.settings import PAGE_SIZE

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


@cache_page(20, key_prefix='index_page')
def index(request):
    """Рендерит страницу со всеми записями из базы данных."""
    template = 'posts/index.html'
    title = 'Последние обновления на сайте'
    post_list = Post.objects.all()
    paginator = Paginator(post_list, PAGE_SIZE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    """Рендерит страницу со всеми записями выбранной группы."""
    template = 'posts/group_list.html'
    title = 'Записи сообщества'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, PAGE_SIZE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': title,
        'page_obj': page_obj,
        'group': group
    }
    return render(request, template, context)


def profile(request, username):
    """Рендерит страничу профиля."""
    title = 'Профайл пользователя'
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=author)
    paginator = Paginator(post_list, PAGE_SIZE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    count_posts = post_list.count()
    context = {
        'title': title,
        'username': username,
        'count_posts': count_posts,
        'page_obj': page_obj,
        'author': author,
    }
    if request.user.is_authenticated:
        check_follow = Follow.objects.filter(
            user=request.user
        ).filter(
            author=author.id
        )
        if check_follow.exists():
            context['following'] = True
        else:
            context['following'] = False
    return render(request, template, context)


def datail(request, post_id):
    """Рендерит страницу подробной информации о посте."""
    template = 'posts/post_datail.html'
    post = get_object_or_404(Post, id=post_id)
    first_30 = post.text[:30]
    title = f'Пост {first_30}'
    author = get_object_or_404(Post, id=post_id)
    count_posts = Post.objects.filter(author=author.author).count()
    comments = post.comment.all()
    form = CommentForm()
    context = {
        'title': title,
        'post': post,
        'count_posts': count_posts,
        'comments': comments,
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    """Рендерит страницу редактирования поста."""
    title = 'Редактирование поста'
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    context = {
        'title': title,
        'is_edit': True,
        'id': post.id,
    }
    if post.author != request.user:
        return redirect('posts:post_datail', post_id=post.id)
    if request.method != 'POST':
        form = PostForm(instance=post)
        context['form'] = form
        return render(request, template, context)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        post.save()
        context['form'] = form
        return redirect('posts:post_datail', post_id=post.id)
    return render(request, template, context)


@login_required
def post_create(request):
    """Рендерит страницу создания поста."""
    title = 'Создание поста'
    template = 'posts/create_post.html'
    context = {
        'title': title,
        'is_edit': False
    }
    form = PostForm(request.POST or None, files=request.FILES or None)
    # Если убрать данную строку проект не проходит тестирование
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            context['form'] = form
            return redirect('posts:profile', username=post.author)
        return render(request, template, context)
    form = PostForm()
    context['form'] = form
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    """Функция для создания комментария."""
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, pk=post_id)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_datail', post_id=post_id)


@login_required
def follow_index(request):
    """Рендерит страницу с постами от авторов на которых подписан
    пользователь."""
    template = 'posts/follow.html'
    title = 'Ваши подписки'
    user = get_object_or_404(User, username=request.user.username)
    author_list = Follow.objects.filter(
        user=user
    ).values_list(
        'author', flat=True
    )
    follow_post_list = Post.objects.filter(author__in=author_list)
    paginator = Paginator(follow_post_list, PAGE_SIZE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """Функция для подписки на автора."""
    author = get_object_or_404(User, username=username)
    check_follow = Follow.objects.filter(
        user=request.user
    ).filter(
        author=author.id
    )
    if not check_follow and username != request.user.username:
        Follow.objects.create(
            user=request.user,
            author=author,
        )
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    """Функция для отписки от автора."""
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user).filter(author=author).delete()
    return redirect('posts:follow_index')
