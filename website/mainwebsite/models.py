from django.db import models

# Create your models here.
class leaderboard(models.Model):
    username = models.CharField(max_length = 32)
    total_played = models.IntegerField()
    top_score = models.IntegerField()
    player_level = models.CharField(max_length = 8)
