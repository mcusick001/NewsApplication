"""
Dedicated URL routing configuration for Django REST Framework
API endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from . import api_views

router = DefaultRouter()
router.register(r'articles', api_views.ArticleViewSet, basename='article')
router.register(
    r'newsletters',
    api_views.NewsletterViewSet,
    basename='newsletter'
)
router.register(
    r'publishers',
    api_views.PublisherViewSet,
    basename='publisher'
)

urlpatterns = [
    path(
        'articles/subscribed/',
        api_views.subscribed_articles,
        name='subscribed_articles'
    ),
    path(
        'approved/',
        api_views.approved_webhook_receiver,
        name='approved_webhook'
    ),
    path('token/', obtain_auth_token, name='api_token_auth'),
    path('', include(router.urls)),
]
