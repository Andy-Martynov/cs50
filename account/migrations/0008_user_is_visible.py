# Generated by Django 2.2.7 on 2021-10-22 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0007_auto_20210227_1811'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_visible',
            field=models.BooleanField(default=True),
        ),
    ]
