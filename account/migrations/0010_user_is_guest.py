# Generated by Django 2.2.7 on 2021-12-20 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0009_remove_user_is_visible'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_guest',
            field=models.BooleanField(default=False),
        ),
    ]
