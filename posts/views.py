from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from posts.forms import CommentForm, PostForm

from .models import Follow, Group, Post, User

from yatube import settings


def index(request):
    # I can't think of one, can you give me a hint?
    posts = Post.objects.all()
    paginator = Paginator(posts, settings.PAGINATOR_PAGE_SIZE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
         request,
         'index.html',
         {'page': page, 'paginator': paginator, 'posts': posts}
     )


def group_posts(request, slug):
    key_group = get_object_or_404(Group, slug=slug)
    posts = key_group.posts.all()
    paginator = Paginator(posts, settings.PAGINATOR_PAGE_SIZE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'group': key_group,
        'posts': posts,
        'slug': slug,
        'page': page,
        'paginator': paginator,
    }

    return render(request, 'group.html', context)


def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.author = request.user
            instance.save()
            return redirect('index')

        return render(request, 'new.html', {'form': form})
    form = PostForm()
    return render(request, 'new.html', {'form': form})


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    user_posts = profile_user.posts.all()
    paginator_profile = Paginator(user_posts, settings.PAGINATOR_PAGE_SIZE)
    page_num_profile = request.GET.get('page')
    page_profile = paginator_profile.get_page(page_num_profile)
    # запрашиваем является ли текущий пользователь подписчиком автора
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=profile_user
        ).exists()
    else:
        following = False
    # считаем количество подписчиков на автора
    roster_followings = Follow.objects.filter(author=profile_user).count()
    # считаем количество подписок автора
    roster_followers = Follow.objects.filter(user=profile_user).count()
    context = {
        'page': page_profile,
        'paginator': paginator_profile,
        'user1': profile_user,
        'post': user_posts,
        'post_author': profile_user,
        'following': following,
        'roster_followings': roster_followings,
        'roster_followers': roster_followers,
    }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    one_post = get_object_or_404(
        Post, author__username=username, id=post_id
    )
    user = get_object_or_404(User, username=username)
    comments = one_post.comments.all()
    count = Post.objects.filter(author=user).count()
    form = CommentForm()
    context = {
        'post': one_post,
        'post_author': one_post.author,
        'post_id': post_id,
        'comments': comments,
        "count": count,
        "form": form,
    }
    return render(request, 'post.html', context)


def post_edit(request, username, post_id):
    post_edit = get_object_or_404(Post, id=post_id, author__username=username)
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post_edit
    )
    if request.user != post_edit.author:
        return redirect('post', username=username, post_id=post_id)
    if form.is_valid():
        form.save()
        return redirect('post', username=username, post_id=post_id)
    context = {
        'form': form,
        'post_edit': post_edit,
        'post_id': post_id,
        'author': post_edit.author,
    }
    return render(request, 'new.html', context)


def page_not_found(request, exception=None):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        form.instance.author = request.user
        form.instance.post = post
        form.save()
    return redirect('post', username, post_id)


@login_required
def follow_index(request):
    # информация о текущем пользователе доступна в переменной request.user
    roster_of_posts = Post.objects.filter(author__following__user=request.user)
    paginator_fol = Paginator(roster_of_posts, settings.PAGINATOR_PAGE_SIZE)
    page_num_fol = request.GET.get('page')
    page = paginator_fol.get_page(page_num_fol)
    context = {
        'page': page,
        'paginator': paginator_fol,
        'user': request.user,
        'post_author': roster_of_posts,
    }
    return render(request, "follow.html", context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author == request.user:
        return redirect('profile', username=username)
    # this method is more concise, thanks!
    Follow.objects.get_or_create(
        author=get_object_or_404(User, username=username),
        user=request.user,
    )
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(
        author=get_object_or_404(User, username=username),
        user=request.user,
    ).delete()
    return redirect('profile', username=username)
