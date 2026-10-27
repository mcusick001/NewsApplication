"""
Serializers for Django REST Framework to convert model instances to JSON
payloads.
"""

from rest_framework import serializers
from .models import CustomUser, Publisher, Article, Newsletter


class UserSerializer(serializers.ModelSerializer):
    """Serializer for CustomUser model."""
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role']


class PublisherSerializer(serializers.ModelSerializer):
    """Serializer for Publisher model."""
    class Meta:
        model = Publisher
        fields = ['id', 'name', 'editors', 'journalists']


class ArticleSerializer(serializers.ModelSerializer):
    """Serializer for Article model with read-only author representation."""
    journalist_username = serializers.CharField(source='journalist.username', read_only=True)  # noqa: E501

    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'publisher', 'journalist_username', 'approved', 'created_at']  # noqa: E501
        read_only_fields = ['journalist']

    def update(self, instance, validated_data):
        """Custom update logic ensuring only editors can modify
        the approval status."""
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user.role == 'editor':  # noqa: E501
            instance.approved = validated_data.get('approved', instance.approved)  # noqa: E501

        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.publisher = validated_data.get('publisher', instance.publisher)  # noqa: E501
        instance.save()
        return instance


class NewsletterSerializer(serializers.ModelSerializer):
    """Serializer for Newsletter model."""
    class Meta:
        model = Newsletter
        fields = ['id', 'title', 'content', 'publisher', 'articles',
                  'created_at']
