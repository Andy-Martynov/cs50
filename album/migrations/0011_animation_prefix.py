# Generated by Django 3.0.8 on 2020-12-26 04:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('album', '0010_auto_20201226_0352'),
    ]

    operations = [
        migrations.AddField(
            model_name='animation',
            name='prefix',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
