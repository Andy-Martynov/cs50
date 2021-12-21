# Generated by Django 2.2.7 on 2021-02-02 01:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('todo', '0004_auto_20210131_1013'),
    ]

    operations = [
        migrations.CreateModel(
            name='Share',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='share_to_me', to='todo.Task')),
                ('who', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='share_i', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
