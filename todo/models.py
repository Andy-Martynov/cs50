from django.db import models

from account.models import User

class Task(models.Model) :
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    parent = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True, related_name="subtasks")
    next = models.ForeignKey("self", on_delete=models.SET_NULL, blank=True, null=True, related_name="prev_task")
    prev = models.ForeignKey("self", on_delete=models.SET_NULL, blank=True, null=True, related_name="next_task")
    name = models.CharField(max_length=200, blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    level = models.IntegerField(default=0)
    checked = models.BooleanField(default=False)
    todo = models.TextField(blank=True, null=True, default="")

    def __str__(self):
        return f"{self.name}"


class Share(models.Model) :
    who = models.ForeignKey(User, on_delete=models.CASCADE, related_name='share_i')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='share_to_me')
    recieved = models.BooleanField(default=False)
    accepted = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    sent = models.BooleanField(default=False)

    def __str__(self):
        if self.recieved:
            recieved = 'recieved'
        else:
            recieved = 'unrecieved'
        if self.accepted:
            accepted = 'accepted'
        else:
            accepted = 'unaccepted'
        if self.rejected:
            rejected = 'rejected'
        else:
            rejected = 'unrejected'

        return f"{self.task.user.username} shares ({self.task.id}) {self.task} to {self.who.username} {recieved} {accepted} {rejected}"


# class ShareReminder(models.Model) :
#     who = models.ForeignKey(User, on_delete=models.CASCADE, related_name='share_reminder_who')
#     to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='share_reminder_to')
#     task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='share_reminder_task')

#     def __str__(self):
#         return f"{self.who} send to ({self.to}) share reminder {self.task}"



