from django.db import models

# Create your models here.
class leaderboard(models.Model):
    rank = models.IntegerField()
    username = models.CharField(max_length = 32)
    total_played = models.IntegerField()
    total_points = models.IntegerField()
    top_score = models.IntegerField()
    avg_score = models.IntegerField()
    player_level = models.CharField(default = "Amateur", max_length = 10)
