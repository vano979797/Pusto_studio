from django.db import models


class Player(models.Model):
    player_id = models.UUIDField(primary_key=True)
    first_login = models.DateTimeField(null=True, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)
    login_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Boost(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    boost_type = models.CharField(max_length=100)
    activated_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(default=0)
