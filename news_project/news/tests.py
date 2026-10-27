"""
Automated integration and unit tests for the News API application.
Covers authentication, RBAC permissions, approval signals, and
webhook receivers.
"""

from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import CustomUser, Publisher, Article

# Create your tests here.


class NewsAPITestCase(APITestCase):
    """Test suite validating end-toend API
    workflows and RBAC security."""

    def setUp(self):
        """Set up test publisher,
        users and authentication endpoints."""
        self.publisher = Publisher.objects.create(name="Daily Planet")

        self.reader = CustomUser.objects.create_user(
            username="reader_user", password="password123", role="reader", email="r@news.com"  # noqa: E501
            )
        self.journalist = CustomUser.objects.create_user(
            username="journalist_user", password="password123", role="journalist", email="j@news.com"  # noqa: E501
            )
        self.editor = CustomUser.objects.create_user(
            username="editor_user", password="password123", role="editor", email="e@news.com"  # noqa: E501
            )

        self.reader.subscriptions_publishers.add(self.publisher)

        self.token_url = reverse('api_token_auth')
        self.article_list_url = reverse('article-list')

    def test_token_authentication(self):
        """Test 1: Validates that correct user credentials
        return an auth token."""
        response = self.client.post(self.token_url, {
            "username": "journalist_user",
            "password": "password123"
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_reader_cannot_create_article(self):
        """Test 2: Enforces RBAC so readers receive 403
        Forbidden when creating articles."""
        self.client.force_authenticate(user=self.reader)
        response = self.client.post(self.article_list_url, {
            "title": "Unauthorized Article",
            "content": "Readers shouldn't be posting news.",
            "publisher": self.publisher.id
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_journalist_can_create_article(self):
        """Test 3: Validates that journalists can create
        draft articles (approved=False)."""
        self.client.force_authenticate(user=self.journalist)
        response = self.client.post(self.article_list_url, {
            "title": "Breaking News",
            "content": "Important investigavite report.",
            "publisher": self.publisher.id
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['approved'], False)

    @patch('news.models.requests.post')
    def test_editor_approval_triggers_signal(self, mock_post):
        """Test 4: Validates editor approval workflow and asynchronous
        webhook dispatching."""
        article = Article.objects.create(
            title="Draft News",
            content="Needs approval.",
            publisher=self.publisher,
            journalist=self.journalist,
            approved=False
        )

        self.client.force_authenticate(user=self.editor)
        detail_url = reverse('article-detail', args=[article.id])

        response = self.client.patch(detail_url, {"approved": True}, format='json')  # noqa: E501

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        article.refresh_from_db()
        self.assertTrue(article.approved)
        mock_post.assert_called_once()

    def test_reader_retrieves_only_subscribed_articles(self):
        """Test 5: Verifies subscription filtering endpoint
        returns correct articles."""
        Article.objects.create(
            title="Subscribed News",
            content="Content here",
            publisher=self.publisher,
            journalist=self.journalist,
            approved=True
        )

        self.client.force_authenticate(user=self.reader)
        subscribed_url = reverse('subscribed_articles')
        response = self.client.get(subscribed_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Subscribed News")

    def test_approved_webhook_receiver(self):
        """Test 6: Validates internal webhook receiver endpoint response."""
        webhook_url = reverse('approved_webhook')
        response = self.client.post(webhook_url, {"article_id": 1, "status": "approved"}, format='json')  # noqa: E501

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "received")
