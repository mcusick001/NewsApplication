"""
API ViewSets and endpoints for DRF serialization
and custom filtering.
"""

from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from .models import Article, Publisher, Newsletter
from .serializers import (
    ArticleSerializer,
    PublisherSerializer,
    NewsletterSerializer
)
from .permissions import (
    IsEditor,
    IsJournalist,
    IsJournalistOrEditor,
    IsArticleAuthorOrEditor
)


class ArticleViewSet(viewsets.ModelViewSet):
    """API endpoint for managing articles with
    RBAC enforcement."""
    serializer_class = ArticleSerializer

    def get_queryset(self):
        """
        Returns articles based on user role.
        Editors and authenticated staff can see all articles (including
        drafts). Readers and unauthenticated users only see approved
        articles.
        """
        user = self.request.user
        if user.is_authenticated:
            if user.role == 'editor' or user.is_staff:
                return Article.objects.all()
            if user.role == 'journalist':
                return Article.objects.filter(
                    Q(approved=True) | Q(journalist=user)
                )
        return Article.objects.filter(approved=True)

    def get_permissions(self):
        """Assigns permissions based on action type."""
        if self.action == 'create':
            permission_classes = [IsJournalist]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsArticleAuthorOrEditor]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """"
        Automatically assigns the logged-in journalist
        and sets approval to False.
        """
        serializer.save(journalist=self.request.user, approved=False)

    def perform_update(self, serializer):
        """
        Prevents journalists from self-approving articles during API
        updates. Only editors can change the approved status to True.
        """
        user = self.request.user
        if user.role == 'journalist':
            # If a journalist attempts to set approved=True, override it
            # to False
            validated_data = serializer.validated_data
            if validated_data.get('approved') is True:
                validated_data['approved'] = False
        serializer.save()


class PublisherViewSet(viewsets.ModelViewSet):
    """API endpoint for publisher management."""
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer

    def get_permissions(self):
        # Only editors can create, update or delete publishers.
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsEditor]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]


class NewsletterViewSet(viewsets.ModelViewSet):
    """API endpoint for newsletter aggregation."""
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer

    def get_permissions(self):
        # Journalists and Editors can create; only editors can update/destroy:
        if self.action in ['create']:
            permission_classes = [IsJournalistOrEditor]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsEditor]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]


@api_view(['POST'])
@permission_classes([AllowAny])
def approved_webhook_receiver(request):
    """Internal webhook receiver endpoint for article
    approval events."""
    article_id = request.data.get('article_id')
    return Response(
        {'status': 'received',
         'message': f'Webhook received for article ID {article_id}'},
        status=200
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subscribed_articles(request):
    user = request.user

    subbed_publishers = user.subscriptions_publishers.all()
    subbed_journalists = user.subscriptions_journalists.all()

    articles = Article.objects.filter(
        publisher__in=subbed_publishers
    ) | Article.objects.filter(
        journalist__in=subbed_journalists
    )

    articles = articles.distinct().filter(approved=True)

    serializer = ArticleSerializer(articles, many=True)
    return Response(serializer.data)
