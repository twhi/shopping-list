# Generated by Django 3.0.7 on 2021-01-09 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20201210_1916'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stopword',
            name='stopword',
            field=models.CharField(max_length=30),
        ),
    ]