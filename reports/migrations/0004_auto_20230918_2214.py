# Generated by Django 3.2.20 on 2023-09-18 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0003_auto_20230918_2208'),
    ]

    operations = [
        migrations.AddField(
            model_name='reports_versions',
            name='reportReviewers',
            field=models.ManyToManyField(related_name='reviewers_versions', to='reports.ReportReviewers'),
        ),
        migrations.AddField(
            model_name='reports_versions',
            name='reviewed',
            field=models.BooleanField(default=False),
        ),
    ]
