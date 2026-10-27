"""
Web forms for user registration and publisher management.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Publisher, Newsletter, Article


class UserRegisterForm(UserCreationForm):
    """Form for registering new users with role selection."""
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role']


class PublisherForm(forms.ModelForm):
    """Form for creating and managing publishers."""
    class Meta:
        model = Publisher
        fields = ['name']


class NewsletterForm(forms.ModelForm):
    """Form for editors to create and edit compiled newsletters."""
    class Meta:
        model = Newsletter
        fields = ['title', 'content', 'publisher', 'articles']
        widgets = {
            'articles': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Security fix: Only allow approved articles to be added to newsletters
        if 'articles' in self.fields:
            self.fields['articles'].queryset = (
                Article.objects.filter(approved=True)
            )

        if 'publisher' in self.fields:
            self.fields['publisher'].required = False
            if user:
                if user.role == 'journalist':
                    self.fields['publisher'].queryset = (
                        Publisher.objects.filter(journalists=user)
                    )
                elif user.role == 'editor':
                    self.fields['publisher'].queryset = (
                        Publisher.objects.filter(editors=user)
                    )


class ArticleForm(forms.ModelForm):
    """Form for journalists to create new articles."""
    class Meta:
        model = Article
        fields = ['title', 'content', 'publisher']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if 'publisher' in self.fields:
            self.fields['publisher'].required = False
            if user and user.role == 'journalist':
                # Journalists only see publishers they are assigned to
                self.fields['publisher'].queryset = (
                    Publisher.objects.filter(journalists=user)
                )
            elif user and user.role == 'editor':
                self.fields['publisher'].queryset = (
                    Publisher.objects.filter(editors=user)
                )
