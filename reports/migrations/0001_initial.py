# Generated by Django 4.2.4 on 2023-09-16 20:24

import ckeditor.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('samples', '0001_initial'),
        ('projects', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('equipment', '0001_initial'),
        ('standardoperatingprotocols', '0001_initial'),
        ('stock', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reports',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('reportBody', ckeditor.fields.RichTextField(blank=True, null=True)),
                ('isEnabled', models.BooleanField()),
                ('ownerSignature', models.CharField(max_length=200)),
                ('creationDate', models.DateField(auto_now_add=True)),
                ('canEditUsers', models.ManyToManyField(related_name='canEditUsers', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ReportsAttachments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(blank=True, null=True, upload_to='documents/%Y/%m/%d')),
            ],
        ),
        migrations.CreateModel(
            name='Tags',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Reports_Versions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, null=True)),
                ('reportBody', ckeditor.fields.RichTextField(blank=True, null=True)),
                ('lastAction', models.CharField(max_length=10)),
                ('lastEditedUserSignature', models.CharField(default='', max_length=200)),
                ('lastEditedDate', models.DateField(auto_now_add=True)),
                ('canEditUsers', models.ManyToManyField(related_name='canEditUsers_versions', to=settings.AUTH_USER_MODEL)),
                ('linkedAttachment', models.ManyToManyField(related_name='linkedAttachment_versions', to='reports.reportsattachments')),
                ('linkedEquipments', models.ManyToManyField(related_name='linkedEquipments_versions', to='equipment.equipment')),
                ('linkedReagents', models.ManyToManyField(related_name='linkedReagents_versions', to='stock.stock')),
                ('linkedReports_versions', models.ManyToManyField(related_name='linkedReports_versions', to='reports.reports')),
                ('linkedSOPs', models.ManyToManyField(related_name='linkedSOPs_versions', to='standardoperatingprotocols.sop')),
                ('linkedSamples', models.ManyToManyField(related_name='linkedSamples_versions', to='samples.sample')),
                ('report', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='reports.reports')),
                ('reportTags', models.ManyToManyField(related_name='linkedTags_versions', to='reports.tags')),
            ],
        ),
        migrations.AddField(
            model_name='reports',
            name='linkedAttachment',
            field=models.ManyToManyField(related_name='linkedAttachment', to='reports.reportsattachments'),
        ),
        migrations.AddField(
            model_name='reports',
            name='linkedEquipments',
            field=models.ManyToManyField(related_name='linkedEquipments', to='equipment.equipment'),
        ),
        migrations.AddField(
            model_name='reports',
            name='linkedReagents',
            field=models.ManyToManyField(related_name='linkedReagents', to='stock.stock'),
        ),
        migrations.AddField(
            model_name='reports',
            name='linkedReports',
            field=models.ManyToManyField(to='reports.reports'),
        ),
        migrations.AddField(
            model_name='reports',
            name='linkedSOPs',
            field=models.ManyToManyField(related_name='linkedSOPs', to='standardoperatingprotocols.sop'),
        ),
        migrations.AddField(
            model_name='reports',
            name='linkedSamples',
            field=models.ManyToManyField(related_name='linkedSamples', to='samples.sample'),
        ),
        migrations.AddField(
            model_name='reports',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='reports',
            name='project',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='projects.projects'),
        ),
        migrations.AddField(
            model_name='reports',
            name='reportTags',
            field=models.ManyToManyField(to='reports.tags'),
        ),
    ]
