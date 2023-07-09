from django import http
from .models import Post, Category, Comment
from django.utils import timezone
from django.urls import reverse_lazy
from .forms import CommentForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from typing import Any, Dict, Optional
from django.db import models
from django.core.paginator import Paginator
from django.forms import modelform_factory
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.views.generic import (
    CreateView, DetailView, UpdateView,
    DeleteView, ListView
)
from django.db.models import Count
from django.http import Http404


class PostMixin:
    model = Post


class PostListView(PostMixin, ListView):
    ordering = '-pub_date'
    paginate_by = 10
    template_name = 'blog/index.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        ).annotate(comment_count=models.Count('comments'))
        return queryset


class PostCreateView(LoginRequiredMixin, PostMixin, CreateView):
    template_name = 'blog/create.html'
    fields = ('title', 'text', 'image', 'pub_date', 'location', 'category')

    def get_success_url(self) -> str:
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, PostMixin, UpdateView):
    template_name = 'blog/create.html'
    fields = ('title', 'text', 'image', 'pub_date', 'location', 'category')

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['pk'])
        if instance.author != request.user:
            return redirect('blog:post_detail', pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self) -> str:
        return reverse_lazy('blog:post_detail',
                            kwargs={'pk': self.kwargs['pk']})


class PostDeleteView(LoginRequiredMixin, PostMixin, DeleteView):
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['pk'])
        if instance.author != request.user:
            return redirect('blog:post_detail', pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self) -> str:
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.object.author.username})

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        form_class = modelform_factory(Post, fields=('title', 'text', 'image'))
        context['form'] = form_class(instance=self.object)
        return context


class CustomLoginView(LoginView):
    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


class PostDetailView(PostMixin, DetailView):
    template_name = 'blog/detail.html'

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, pk=self.kwargs["pk"])
        if not post.is_published or not post.category.is_published or post.pub_date > timezone.now():
            if self.request.user != post.author:
                raise Http404("Post does not exist")

        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = Comment.objects.filter(post=self.object)
        return context


def category_posts_view(request, category_slug):
    category = get_object_or_404(Category.objects.filter(slug=category_slug,
                                                         is_published=True))
    queryset = Post.objects.filter(category=category, is_published=True,
                                   pub_date__lte=timezone.now()
                                   ).order_by('-pub_date').annotate(
        comment_count=models.Count('comments'))

    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'category': category,
               'page_obj': page_obj, }
    return render(request, 'blog/category.html', context)


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        form.instance.post = post
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'pk': self.kwargs['post_id']})


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_queryset(self):
        return Comment.objects.filter(
            id=self.kwargs['pk'], author=self.request.user)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'pk': self.kwargs['post_id']})


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    context_object_name = 'comment'

    def get_queryset(self):
        return Comment.objects.filter(
            id=self.kwargs['pk'], author=self.request.user)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'pk': self.kwargs['post_id']})


class ProfileMixin:
    model = User
    form_class = UserCreationForm


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    fields = ('username', 'first_name', 'last_name', 'email')

    def get_success_url(self) -> str:
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.object.username})

    def get_object(self, queryset=None):
        return get_object_or_404(User, username=self.kwargs.get('username'))

    def form_valid(self, form):
        user = form.save(commit=False)
        user.username = form.cleaned_data.get('username')
        self.request.user = user
        user.save()
        return redirect(self.get_success_url())


class ProfileDetailView(PostMixin, ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        self.user = get_object_or_404(User, username=self.kwargs['username'])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        if self.kwargs["username"] == self.request.user.username:
            return Post.objects.filter(
                author=self.request.user,
            ).order_by("-pub_date") \
             .annotate(comment_count=Count("comments"))
        else:
            return Post.objects.filter(
                author__username=self.kwargs["username"],
                category__is_published=True,
                pub_date__lte=timezone.now(),
                is_published=True
            ).order_by("-pub_date") \
             .annotate(comment_count=Count("comments"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.user

        return context
