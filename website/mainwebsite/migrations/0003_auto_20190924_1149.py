# Generated by Django 2.2.3 on 2019-09-24 06:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mainwebsite', '0002_delete_users'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='leaderboard',
            name='avg_score',
        ),
        migrations.RemoveField(
            model_name='leaderboard',
            name='total_points',
        ),
    ]
