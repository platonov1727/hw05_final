from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Group, Post, Follow, Comment

User = get_user_model()

POSTS_PER_PAGE = 10
CACHE_TIME_SEC = 20


def get_page(request, post_list):
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


@cache_page(CACHE_TIME_SEC, key_prefix='index_page')
def index(request):
    template = 'posts/index.html'
    title = "Это главная страница проекта Yatube."
    text = "Последние обновления на сайте"
    post_list = Post.objects.all()
    page_obj = get_page(request, post_list)
    context = {'title': title, 'text': text, 'page_obj': page_obj}
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    title = 'Записи сообщества'
    post_list = Post.objects.filter(group=group)
    page_obj = get_page(request, post_list)
    context = {'group': group, 'title': title, 'page_obj': page_obj}
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    title = 'Профайл пользователя'
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page_obj = get_page(request, posts)
    following = Follow.objects.filter(user__username=request.user,
                                      author=author)
    followers_count = Follow.objects.filter(author=author).count()
    followings_count = Follow.objects.filter(user=author).count()
    context = {
        'followers_count': followers_count,
        'followings_count': followings_count,
        'page_obj': page_obj,
        'author': author,
        'following': following,
        'posts': posts,
        'title': title
    }
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post.objects.select_related('author', 'group'),
                             id=post_id)
    template = 'posts/post_detail.html'
    form = CommentForm(request.POST or None)
    comments = post.comments.all()

    context = {'form': form, 'comments': comments, 'post': post}

    return render(request, template, context)


@login_required
def post_create(request):
    title = 'Новый пост'
    form = PostForm(request.POST or None, files=request.FILES or None)

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=post.author.username)
    return render(request, 'posts/create.html', {'form': form, 'title': title})


@login_required()
def post_edit(request, post_id):
    template = 'posts/create.html'
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = Post.objects.get(id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    title = 'Избранные авторы'
    text = 'Страница избранных авторов'
    post_list = Post.objects.filter(author__following__user=request.user)
    page_obj = get_page(request, post_list)
    context = {'title': title, 'text': text, 'page_obj': page_obj}
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user == author:
        return redirect('posts:profile', username=username)
    Follow.objects.get_or_create(author=author, user=request.user)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    is_follower = Follow.objects.filter(user=request.user, author=author)
    if is_follower.exists():
        is_follower.delete()
    return redirect('posts:profile', username=username)

@login_required
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post_id = comment.post_id
    if request.user.username == comment.author.username:
        comment.delete()
    return redirect('posts:post_detail', post_id=post_id)
