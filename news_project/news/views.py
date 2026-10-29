"""
Front-end web views for authentication, dashboards,
and role-based workflows.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from .models import Article, Publisher, CustomUser, Newsletter
from .forms import UserRegisterForm, PublisherForm, NewsletterForm, ArticleForm
from .decorators import role_required

# Create your views here.


def register_view(request):
    """Handles new user registration."""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard_redirect')
    else:
        form = UserRegisterForm()
    return render(request, 'news/register.html', {'form': form})


def login_view(request):
    """Handles user login."""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard_redirect')
    else:
        form = AuthenticationForm()
    return render(request, 'news/login.html', {'form': form})


def article_feed(request):
    """Displays public approved articles and newsletters."""
    articles = Article.objects.filter(
        approved=True
    ).order_by('-created_at')
    newsletters = Newsletter.objects.all().order_by('-created_at')
    return render(request, 'news/article_feed.html', {
        'articles': articles,
        'newsletters': newsletters,
    })


@login_required
def dashboard_redirect(request):
    """Routes users to their role-specific dashboard."""
    if request.user.role == 'editor':
        return redirect('editor_dashboard')
    elif request.user.role == 'journalist':
        return redirect('journalist_dashboard')
    elif request.user.role == 'reader':
        return redirect('reader_dashboard')
    return redirect('article_feed')


@login_required
@role_required(['editor'])
def editor_dashbaord(request):
    """Displays pending articles and newsletters for editor
    review and management."""
    assigned_publishers = request.user.managed_publishers.all()
    articles = Article.objects.filter(
        Q(publisher__in=assigned_publishers)
        | Q(publisher__isnull=True)
    )  # Editors can manage all articles
    newsletters = Newsletter.objects.filter(
        Q(publisher__in=assigned_publishers)
        | Q(publisher__isnull=True)
    )
    return render(request, 'news/editor_dashboard.html', {
        'articles': articles,
        'newsletters': newsletters
    })


@login_required
@role_required(['editor'])
def approve_article(request, pk):
    """Approves an article from the editor dashboard."""
    article = get_object_or_404(Article, pk=pk)
    if (article.publisher and
            not article.publisher.editors.filter(id=request.user.id).exists()):
        return redirect('editor_dashboard')
    if request.method == 'POST':
        article.approved = True
        article.save()
    return redirect('editor_dashboard')


@login_required
@role_required(['editor', 'journalist'])
def create_newsletter(request):
    """Allows editors and journalists to create a new compiled newsletter."""
    if request.method == 'POST':
        form = NewsletterForm(request.POST, user=request.user)
        if form.is_valid():
            newsletter = form.save(commit=False)
            newsletter.author = request.user
            newsletter.save()
            form.save_m2m()
            return redirect(
                'editor_dashboard'
                if request.user.role == 'editor'
                else 'journalist_dashboard'
            )
    else:
        form = NewsletterForm(user=request.user)
    return render(request, 'news/newsletter_form.html', {'form': form})


@login_required
@role_required(['editor', 'journalist'])
def edit_newsletter(request, pk):
    """Allows editors or the newsletter author to
    edit an existing newsletter."""
    newsletter = get_object_or_404(Newsletter, pk=pk)
    if request.user.role != 'editor' and newsletter.author != request.user:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        form = NewsletterForm(
            request.POST,
            instance=newsletter,
            user=request.user
        )
        if form.is_valid():
            form.save()
            return redirect(
                'editor_dashboard'
                if request.user.role == 'editor'
                else 'journalist_dashboard'
            )
    else:
        form = NewsletterForm(instance=newsletter, user=request.user)
    return render(request, 'news/newsletter_form.html', {
        'form': form,
        'newsletter': newsletter
    })


@login_required
@role_required(['editor', 'journalist'])
def delete_newsletter(request, pk):
    """Allows editors or authors to delete a newsletter."""
    newsletter = get_object_or_404(Newsletter, pk=pk)
    if request.user.role != 'editor' and newsletter.author != request.user:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        newsletter.delete()
        return redirect(
            'editor_dashboard'
            if request.user.role == 'editor'
            else 'journalist_dashboard'
        )
    return render(
        request,
        'news/newsletter_confirm_delete.html',
        {'newsletter': newsletter},
    )


@login_required
@role_required(['journalist'])
def create_article(request):
    """Allows journalists to create a new article for review."""
    if request.method == 'POST':
        form = ArticleForm(request.POST, user=request.user)
        if form.is_valid():
            article = form.save(commit=False)
            # Automatically assign logged-in user
            article.journalist = request.user
            article.approved = False  # Must be reviewed by an editor
            # Ensure publisher is safely set to None if omitted or optional
            if not getattr(article, 'publisher', None):
                article.publisher = None
            article.save()
            return redirect('journalist_dashboard')
    else:
        form = ArticleForm(user=request.user)
    return render(request, 'news/article_form.html', {'form': form})


@login_required
@role_required(['editor', 'journalist'])
def edit_article(request, pk):
    """Allows editors or the article's journalist author
    to update the article."""
    article = get_object_or_404(Article, pk=pk)
    if request.user.role != 'editor' and article.journalist != request.user:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article, user=request.user)
        if form.is_valid():
            form.save()
            return redirect(
                'editor_dashboard'
                if request.user.role == 'editor'
                else 'journalist_dashboard'
            )
    else:
        form = ArticleForm(instance=article, user=request.user)
    return render(
        request, 'news/article_form.html', {'form': form, 'article': article}
    )


@login_required
@role_required(['editor', 'journalist'])
def delete_article(request, pk):
    """Allows editors or the article's journalist author
    to delete an article."""
    article = get_object_or_404(Article, pk=pk)
    if request.user.role != 'editor' and article.journalist != request.user:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        article.delete()
        return redirect(
            'editor_dashboard'
            if request.user.role == 'editor'
            else 'journalist_dashboard'
        )
    return render(
        request, 'news/article_confirm_delete.html', {'article': article}
    )


@login_required
@role_required(['journalist'])
def journalist_dashboard(request):
    """Displays articles authored by the logged-in
    journalist."""
    articles = Article.objects.filter(journalist=request.user)
    newsletters = Newsletter.objects.filter(author=request.user)
    return render(request, 'news/journalist_dashboard.html', {
        'articles': articles,
        'newsletters': newsletters,
    })


@login_required
@role_required(['reader'])
def reader_dashboard(request):
    """Personalized landing page for readers showing articles
    and newsletters from their subscriptions."""
    pub_subs = request.user.subscriptions_publishers.all()
    jour_subs = request.user.subscriptions_journalists.all()

    # Filter approved articles from subscribed publishers or journalists
    articles = Article.objects.filter(approved=True).filter(
        Q(publisher__in=pub_subs) | Q(journalist__in=jour_subs)
    ).distinct().order_by('-created_at')

    # Filter newsletters from subscribed publishers
    newsletters = Newsletter.objects.filter(
        Q(publisher__in=pub_subs) | Q(author__in=jour_subs)
    ).distinct().order_by('-created_at')

    return render(request, 'news/reader_dashboard.html', {
        'articles': articles,
        'newsletters': newsletters,
    })


@login_required
@role_required(['reader'])
def manage_subscriptions(request):
    """Allows readers to toggle publisher and journalist subscriptions."""
    publishers = Publisher.objects.all()
    journalists = CustomUser.objects.filter(role='journalist')

    if request.method == 'POST':
        request.user.subscriptions_publishers.set(
            request.POST.getlist('publishers')
        )
        request.user.subscriptions_journalists.set(
            request.POST.getlist('journalists')
        )
        return redirect('reader_subscriptions')

    return render(request, 'news/subscriptions.html', {
        'publishers': publishers,
        'journalists': journalists,
    })


@login_required
@role_required(['editor'])  # Strictly editors only.
def manage_publishers(request):
    """Allows creation and management of publishers (Restricted to Editors)."""
    if request.method == 'POST':
        form = PublisherForm(request.POST)
        if form.is_valid():
            publisher = form.save()
            # Automatically assign the creating editor to the new publisher
            publisher.editors.add(request.user)
            return redirect('manage_publishers')
    else:
        form = PublisherForm()

    publishers = Publisher.objects.all()
    return render(request, 'news/publisher_management.html', {
        'form': form,
        'publishers': publishers
    })
