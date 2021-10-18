from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from yatube.settings import PAGE_SIZE

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def collect_paginator(post_list, request):
    paginator = Paginator(post_list, PAGE_SIZE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


@cache_page(20, key_prefix='index_page')
def index(request):
    """Рендерит страницу со всеми записями из базы данных."""
    template = 'posts/index.html'
    post_list = Post.objects.all()
    page_obj = collect_paginator(post_list, request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    """Рендерит страницу со всеми записями выбранной группы."""
    template = 'posts/group_list.html'
    title = 'Записи сообщества'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = collect_paginator(post_list, request)
    context = {
        'title': title,
        'page_obj': page_obj,
        'group': group
    }
    return render(request, template, context)


def profile(request, username):
    """Рендерит страничу профиля."""
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=author)
    page_obj = collect_paginator(post_list, request)
    count_posts = post_list.count()
    following = False
    # Условия не получится объединить, так как сначало нужно узнать
    # авторизован ли пользователь. Если делать это условие вместе, то
    # check_follow будет выбивать ошибку
    if request.user.is_authenticated:
        check_follow = Follow.objects.filter(
            user=request.user,
            author=author.id
        )
        if check_follow.exists():
            following = True
    context = {
        'username': username,
        'count_posts': count_posts,
        'page_obj': page_obj,
        'author': author,
        'following': following
    }
    return render(request, template, context)


def datail(request, post_id):
    """Рендерит страницу подробной информации о посте."""
    template = 'posts/post_datail.html'
    post = get_object_or_404(Post, id=post_id)
    author = get_object_or_404(Post, id=post_id)
    count_posts = Post.objects.filter(author=author.author).count()
    comments = post.comment.all()
    form = CommentForm()
    context = {
        'post': post,
        'count_posts': count_posts,
        'comments': comments,
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    """Рендерит страницу редактирования поста."""
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_datail', post_id=post.id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_datail', post_id=post.id)
    context = {
        'is_edit': True,
        'id': post.id,
        'form': form
    }
    return render(request, template, context)


@login_required
def post_create(request):
    """Рендерит страницу создания поста."""
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=post.author)
    context = {
        'is_edit': False,
        'form': form,
    }
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
    user = get_object_or_404(User, username=request.user.username)
    author_list = Follow.objects.filter(
        user=user
    ).values_list(
        'author', flat=True
    )
    follow_post_list = Post.objects.filter(author__in=author_list)
    page_obj = collect_paginator(follow_post_list, request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """Функция для подписки на автора."""
    author = get_object_or_404(User, username=username)
    user = request.user
    if author != user:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    """Функция для отписки от автора."""
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:follow_index')
