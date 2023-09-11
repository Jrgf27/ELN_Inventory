# Generated by Django 3.2.20 on 2023-08-15 21:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('standardoperatingprotocols', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('riskassessments', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(null=True)),
                ('origin', models.CharField(max_length=200, null=True)),
                ('supportContact', models.CharField(max_length=200, null=True)),
                ('isEnabled', models.BooleanField(default=True)),
                ('relatedRiskAssessment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='riskassessments.riskassessment')),
                ('relatedSOP', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='standardoperatingprotocols.sop')),
                ('responsibleUser', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Equipment_Versions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('origin', models.CharField(max_length=200, null=True)),
                ('supportContact', models.CharField(max_length=200, null=True)),
                ('lastAction', models.CharField(max_length=10)),
                ('lastEditedUserSignature', models.CharField(max_length=200)),
                ('lastEditedDate', models.DateField(auto_now_add=True)),
                ('equipment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='equipment.equipment')),
                ('relatedRiskAssessment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='riskassessments.riskassessment')),
                ('relatedSOP', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='standardoperatingprotocols.sop')),
                ('responsibleUser', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]