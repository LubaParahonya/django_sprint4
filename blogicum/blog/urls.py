from django.urls import path
from django.contrib.auth.views import (PasswordChangeView,
                                       PasswordChangeDoneView)
from . import views


app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),

    path('posts/create/', views.PostCreateView.as_view(),
         name='create_post'),
    path('posts/<int:pk>/edit/', views.PostUpdateView.as_view(),
         name='edit_post'),
    path('posts/<int:pk>/delete/', views.PostDeleteView.as_view(),
         name='delete_post'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(),
         name='post_detail'),
    path('posts/<int:post_id>/comment/', views.CommentCreateView.as_view(),
         name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:pk>/',
         views.CommentUpdateView.as_view(), name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:pk>/',
         views.CommentDeleteView.as_view(), name='delete_comment'),
    path('profile/<str:username>/', views.ProfileDetailView.as_view(),
         name='profile'),
    path('profile/<str:username>/edit/', views.ProfileUpdateView.as_view(),
         name='edit_profile'),
    path('profile/<str:username>/password_change/',
         PasswordChangeView.as_view(),
         name='password_change'),
    path('profile/<str:username>/password_change/done/',
         PasswordChangeDoneView.as_view(),
         name='password_change'),
    path('category/<slug:category_slug>/', views.category_posts_view,
         name='category_posts'),
]
