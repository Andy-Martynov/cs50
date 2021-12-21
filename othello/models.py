from django.db import models

from game.models import Game

dflt = '0000000000000000000000000000000000000000000000000000000000000000'

class OthelloPos(models.Model):
    game =          models.OneToOneField(Game, on_delete=models.CASCADE)
    pos1 =          models.CharField(max_length=64, default=dflt)
    pos2 =          models.CharField(max_length=64, default=dflt)

    def __str__(self):
        return f'{self.game.id}, {self.pos1}, {self.pos2}'