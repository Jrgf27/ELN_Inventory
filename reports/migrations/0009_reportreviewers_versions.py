# Generated by Django 3.2.20 on 2023-09-18 22:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reports', '0008_alter_reportreviewers_reviewersignature'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReportReviewers_Versions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reviewDecision', models.CharField(default='', max_length=10)),
                ('reviewed', models.BooleanField(default=False)),
                ('reviewerSignature', models.CharField(blank=True, default='', max_length=200, null=True)),
                ('lastAction', models.CharField(max_length=10)),
                ('lastEditedUserSignature', models.CharField(default='', max_length=200)),
                ('lastEditedDate', models.DateField(auto_now_add=True)),
                ('reviewer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
