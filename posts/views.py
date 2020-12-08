from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page


from posts.forms import PostForm, PostComment
from .models import Group, Post, User


def index(request):
    posts = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(posts, 10)
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
    paginator = Paginator(posts, 10)
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
    paginator_profile = Paginator(user_posts, 10)
    page_num_profile = request.GET.get('page')
    page_profile = paginator_profile.get_page(page_num_profile)
    context = {
        'page': page_profile,
        'paginator': paginator_profile,
        'user1': profile_user,
        'post': user_posts,
        'post_author': profile_user,
    }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    one_post = get_object_or_404(
        Post, author__username=username, id=post_id
    )
    user = get_object_or_404(User, username=username)
    comments = one_post.comments.all()
    count = Post.objects.filter(author=user).count()
    form = PostComment()
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
    form = PostComment(request.POST or None)
    if form.is_valid():
        form.instance.author = request.user
        form.instance.post = post
        form.save()
        return redirect('post', username, post_id)

