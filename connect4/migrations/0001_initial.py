# Generated by Django 2.2.7 on 2021-12-18 09:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('game', '0008_player_kind'),
    ]

    operations = [
        migrations.CreateModel(
            name='Connect4Pos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pos1', models.BigIntegerField(default=0)),
                ('pos2', models.BigIntegerField(default=0)),
                ('game', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='game.Game')),
            ],
        ),
    ]