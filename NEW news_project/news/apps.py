from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_groups_and_permissions(sender, **kwargs):
    from django.contrib.auth.models import Group, Permission
    from django.contrib.contenttypes.models import ContentType
    from .models import Article, Newsletter

    reader_group, _ = Group.objects.get_or_create(name='Reader')
    editor_group, _ = Group.objects.get_or_create(name='Editor')
    journalist_group, _ = Group.objects.get_or_create(name='Journalist')

    article_ct = ContentType.objects.get_for_model(Article)
    newsletter_ct = ContentType.objects.get_for_model(Newsletter)

    view_art = Permission.objects.get(codename='view_article', content_type=article_ct)  # noqa: E501
    add_art = Permission.objects.get(codename='add_article', content_type=article_ct)  # noqa: E501
    change_art = Permission.objects.get(codename='change_article', content_type=article_ct)  # noqa: E501
    delete_art = Permission.objects.get(codename='delete_article', content_type=article_ct)  # noqa: E501

    view_news = Permission.objects.get(codename='view_newsletter', content_type=newsletter_ct)  # noqa: E501
    add_news = Permission.objects.get(codename='add_newsletter', content_type=newsletter_ct)  # noqa: E501
    change_news = Permission.objects.get(codename='change_newsletter', content_type=newsletter_ct)  # noqa: E501
    delete_news = Permission.objects.get(codename='delete_newsletter', content_type=newsletter_ct)  # noqa: E501

    reader_group.permissions.set([view_art, view_news])

    editor_group.permissions.set([
        view_art, change_art, delete_art,
        view_news, change_news, delete_news
    ])

    journalist_group.permissions.set([
        view_art, add_art, change_art, delete_art,
        view_news, add_news, change_news, delete_news
    ])


class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'

    def ready(self):
        post_migrate.connect(create_groups_and_permissions, sender=self)
