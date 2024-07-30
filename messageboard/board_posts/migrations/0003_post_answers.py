# Generated by Django 5.0.4 on 2024-07-30 10:00

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board_posts', '0002_alter_post_text'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='answers',
            field=models.ManyToManyField(blank=True, related_name='answered_posts', to=settings.AUTH_USER_MODEL),
        ),
    ]
