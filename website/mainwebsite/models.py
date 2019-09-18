from django.db import models

# Create your models here.
class users(models.Model):
    username = models.CharField()
    password = models.CharField()

class leaderboard(models.Model):
    rank = models.IntegerField()
    username = models.CharField()
    total_played = models.IntegerField()
    total_points = models.IntegerField()
    top_score = models.IntegerField()
    avg_score = models.IntegerField()
    player_level = models.CharField(default = "Amateur")
