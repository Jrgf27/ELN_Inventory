# Generated by Django 3.2.20 on 2023-08-23 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='projects',
            name='isEnabled',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
    ]