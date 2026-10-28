"""
URL routing configuration for API endpoints and web views.
"""

from django.urls import path, include
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    # Blank root path resolving http://localhost:8000/ to the article feed
    path('', views.article_feed, name='article_feed'),

    # Include API routes under the api/ prefix
    path('api/', include('news.api_urls')),

    # Front-End UI Views & Dashboards
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
    path('dashboard/editor/', views.editor_dashbaord, name='editor_dashboard'),
    path('dashboard/reader/', views.reader_dashboard, name='reader_dashboard'),
    path('article/create/', views.create_article, name='create_article'),
    path('article/edit/<int:pk>/', views.edit_article, name='edit_article'),
    path(
        'article/delete/<int:pk>/',
        views.delete_article,
        name='delete_article'
    ),
    path(
        'article/publish/<int:pk>/',
        views.publish_independent_article,
        name='publish_independent_article'
    ),
    path(
        'editor/approve/<int:pk>/',
        views.approve_article,
        name='approve_article'
    ),
    path(
        'newsletter/create/',
        views.create_newsletter,
        name='create_newsletter'
    ),
    path(
        'newsletter/edit/<int:pk>/',
        views.edit_newsletter,
        name='edit_newsletter'
    ),
    path(
        'newsletter/delete/<int:pk>/',
        views.delete_newsletter,
        name='delete_newsletter'
    ),
    path(
        'dashboard/journalist/',
        views.journalist_dashboard,
        name='journalist_dashboard'
    ),
    path(
        'subscriptions/',
        views.manage_subscriptions,
        name='reader_subscriptions'
    ),
    path(
        'publishers/manage/',
        views.manage_publishers,
        name='manage_publishers'
    ),
    path('articles/', views.article_feed, name='article_feed'),
    path(
        'logout/',
        LogoutView.as_view(next_page='login'),
        name='logout'
    ),
]
