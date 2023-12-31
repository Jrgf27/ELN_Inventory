# Generated by Django 4.2.4 on 2023-09-16 20:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ItemCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('isEnabled', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='ItemCategory_Versions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('lastAction', models.CharField(max_length=10)),
                ('lastEditedUserSignature', models.CharField(default='', max_length=200)),
                ('lastEditedDate', models.DateField(auto_now_add=True)),
                ('itemCategory', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='itemcategory.itemcategory')),
            ],
        ),
    ]
