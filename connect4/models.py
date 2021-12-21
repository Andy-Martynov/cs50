from django.db import models

from game.models import Game

class Connect4Pos(models.Model):
    game =          models.OneToOneField(Game, on_delete=models.CASCADE, related_name='pos')
    one =          models.BigIntegerField(default=0)
    two =          models.BigIntegerField(default=0)

    def __str__(self):
        return f'{self.game.id}, {self.pos1}, {self.pos2}'