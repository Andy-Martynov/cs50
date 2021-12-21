from django.db import models

from account.models import User

class GameKind(models.Model):
    name =          models.CharField(max_length=20, default='game')
    image =         models.ImageField(upload_to="game/images/", blank=True, null=True)

    def __str__(self):
        return f"{self.name}"


class Player(models.Model):
    user =         models.OneToOneField(User, on_delete=models.CASCADE)
    is_bot =       models.BooleanField(default=False)
    kind =         models.ForeignKey(GameKind, on_delete=models.CASCADE, null=True, blank=True, related_name='bots')
    is_playing =   models.BooleanField(default=False)
    ready =        models.BooleanField(default=False)
    rating =       models.FloatField(default=0)
    games =        models.IntegerField(default=0)
    win =          models.IntegerField(default=0)
    loss =         models.IntegerField(default=0)
    tie =          models.IntegerField(default=0)

    def __str__(self):
        bot = ''
        if self.is_bot:
            bot = ' BOT'
        return f"{self.user.id}{bot} {self.user.username}, <{int(self.rating)}>"

    def name(self):
        return self.user.username.replace('_', ' ')

    def serialize(self):
        return {
            "id": self.user.id,
            "username": self.user.username,
            'image': self.user.image,
        }


class Game(models.Model):
    kind =          models.ForeignKey(GameKind, on_delete=models.CASCADE, related_name='games')
    gameover =      models.BooleanField(default=False)
    first =         models.ForeignKey(Player, on_delete=models.CASCADE, related_name='first_games')
    second =        models.ForeignKey(Player, on_delete=models.CASCADE, related_name='second_games')
    current =       models.ForeignKey(Player, on_delete=models.CASCADE, null=True, blank=True) # , related_name='second_games')
    step =          models.IntegerField(default=0)
    winner =        models.ForeignKey(Player, on_delete=models.CASCADE, null=True, blank=True, related_name='winned_games')
    loser =         models.ForeignKey(Player, on_delete=models.CASCADE, null=True, blank=True, related_name='lost_games')
    is_finished =   models.BooleanField(default=False)
    moves =         models.CharField(max_length=200, default='')
    timestamp =     models.DateTimeField(auto_now_add=True)
    hints =         models.BooleanField(default=False)
    delta1 =        models.FloatField(default=0)
    delta2 =        models.FloatField(default=0)

    def __str__(self):
        if self.is_finished:
            if self.winner:
                if self.winner == self.first:
                    return f"{self.id} {self.first.user.username} win (+{int(self.delta1)}) : {self.second.user.username} loss ({int(self.delta2)})>"
                else:
                    return f"{self.id} {self.first.user.username} loss ({int(self.delta1)}) : {self.second.user.username} win (+{int(self.delta2)})>"
            else:
                return f"{self.id} {self.first.user.username} tie ({+int(self.delta1)}) : {self.second.user.username} tie (+{int(self.delta2)})>"
        else:
            return f"{self.id} {self.first.user.username} : {self.second.user.username}"

