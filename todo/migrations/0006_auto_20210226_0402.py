# Generated by Django 2.2.7 on 2021-02-26 04:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0005_share'),
    ]

    operations = [
        migrations.AddField(
            model_name='share',
            name='accepted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='share',
            name='recieved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='share',
            name='rejected',
            field=models.BooleanField(default=False),
        ),
    ]
