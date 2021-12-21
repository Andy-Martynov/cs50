# Generated by Django 2.2.7 on 2021-12-13 15:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AbstractPlayer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_bot', models.BooleanField(default=False)),
                ('is_playing', models.BooleanField(default=False)),
                ('ready', models.BooleanField(default=False)),
                ('rating', models.FloatField(default=600)),
                ('games', models.IntegerField(default=0)),
                ('win', models.IntegerField(default=0)),
                ('loss', models.IntegerField(default=0)),
                ('tie', models.IntegerField(default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AbstractGame',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='game', max_length=20)),
                ('gameover', models.BooleanField(default=False)),
                ('step', models.IntegerField(default=0)),
                ('is_finished', models.BooleanField(default=False)),
                ('moves', models.CharField(default='', max_length=200)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('hints', models.BooleanField(default=False)),
                ('delta1', models.FloatField(default=0)),
                ('delta2', models.FloatField(default=0)),
                ('current', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='game.AbstractPlayer')),
                ('first', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='first_games', to='game.AbstractPlayer')),
                ('loser', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='lost_games', to='game.AbstractPlayer')),
                ('second', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='second_games', to='game.AbstractPlayer')),
                ('winner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='winned_games', to='game.AbstractPlayer')),
            ],
        ),
    ]