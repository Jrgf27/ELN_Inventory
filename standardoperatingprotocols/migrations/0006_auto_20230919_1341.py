# Generated by Django 3.2.20 on 2023-09-19 12:41

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('standardoperatingprotocols', '0005_auto_20230919_1338'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sop_versions',
            name='trainee',
        ),
        migrations.AddField(
            model_name='sop_versions',
            name='trainee',
            field=models.ManyToManyField(related_name='trainee_versions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.RemoveField(
            model_name='sop_versions',
            name='trainer',
        ),
        migrations.AddField(
            model_name='sop_versions',
            name='trainer',
            field=models.ManyToManyField(related_name='trainer_versions', to=settings.AUTH_USER_MODEL),
        ),
    ]