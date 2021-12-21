# Generated by Django 2.2.7 on 2021-01-31 09:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0002_auto_20210130_1910'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='next',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='prev', to='todo.Task'),
        ),
        migrations.AlterField(
            model_name='task',
            name='todo',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]