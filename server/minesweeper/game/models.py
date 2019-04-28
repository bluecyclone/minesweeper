from django.db import models

class Board(models.Model):
    id = models.AutoField(primary_key=True)
    data = models.CharField(max_length=1000)
    board = models.TextField()
    width = models.IntegerField()
    height = models.IntegerField()
    state = models.CharField(max_length=200)
    mines = models.IntegerField()