# Generated by Django 3.0.5 on 2020-05-04 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20200427_1743'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='name',
            field=models.CharField(max_length=24),
        ),
        migrations.AlterField(
            model_name='item',
            name='quantity',
            field=models.CharField(max_length=12),
        ),
    ]
