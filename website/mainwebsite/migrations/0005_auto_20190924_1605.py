# Generated by Django 2.2.5 on 2019-09-24 16:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainwebsite', '0004_remove_leaderboard_rank'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leaderboard',
            name='player_level',
            field=models.CharField(max_length=8),
        ),
    ]
