# Generated by Django 4.2.4 on 2023-09-16 20:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('item', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Suppliers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('website', models.URLField()),
                ('phoneNumber', models.CharField(max_length=20)),
                ('emailAddress', models.CharField(max_length=200)),
                ('contactName', models.CharField(max_length=200)),
                ('isEnabled', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='SuppliersItems',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('website', models.URLField()),
                ('supplierProductCode', models.CharField(max_length=200)),
                ('isEnabled', models.BooleanField(default=True)),
                ('itemId', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='item.items')),
                ('supplierId', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='supplier.suppliers')),
            ],
        ),
        migrations.CreateModel(
            name='SuppliersItems_Versions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('website', models.URLField()),
                ('supplierProductCode', models.CharField(max_length=200)),
                ('lastAction', models.CharField(max_length=10)),
                ('lastEditedUserSignature', models.CharField(default='', max_length=200)),
                ('lastEditedDate', models.DateField(auto_now_add=True)),
                ('itemId', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='item.items')),
                ('supplierId', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='supplier.suppliers')),
                ('supplierItem', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='supplier.suppliersitems')),
            ],
        ),
        migrations.CreateModel(
            name='Suppliers_Versions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('website', models.URLField()),
                ('phoneNumber', models.CharField(max_length=20)),
                ('emailAddress', models.CharField(max_length=200)),
                ('contactName', models.CharField(max_length=200)),
                ('lastAction', models.CharField(max_length=10)),
                ('lastEditedUserSignature', models.CharField(default='', max_length=200)),
                ('lastEditedDate', models.DateField(auto_now_add=True)),
                ('supplier', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='supplier.suppliers')),
            ],
        ),
    ]
