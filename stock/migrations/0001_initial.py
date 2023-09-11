# Generated by Django 3.2.20 on 2023-08-15 21:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('supplier', '0001_initial'),
        ('location', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('batchCode', models.CharField(blank=True, max_length=200, null=True)),
                ('quantity', models.IntegerField()),
                ('hasBatchCode', models.BooleanField()),
                ('isEnabled', models.BooleanField(default=True)),
                ('itemId', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='supplier.suppliersitems')),
                ('locationId', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.locations')),
            ],
        ),
        migrations.CreateModel(
            name='Stock_Versions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('batchCode', models.CharField(blank=True, max_length=200, null=True)),
                ('quantity', models.IntegerField()),
                ('hasBatchCode', models.BooleanField()),
                ('lastAction', models.CharField(max_length=10)),
                ('lastEditedUserSignature', models.CharField(default='', max_length=200)),
                ('lastEditedDate', models.DateField(auto_now_add=True)),
                ('itemId', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='supplier.suppliersitems')),
                ('locationId', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.locations')),
                ('stock', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='stock.stock')),
            ],
        ),
    ]