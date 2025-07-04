from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ticker = models.CharField(max_length=10)
    next_day_price = models.FloatField()
    mse = models.FloatField()
    rmse = models.FloatField()
    r2 = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    plot_1 = models.ImageField(upload_to='plots/')
    plot_2 = models.ImageField(upload_to='plots/')

    def __str__(self):
        return f"{self.ticker} - {self.user.username} - {self.created_at.date()}"


class TelegramUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    chat_id = models.BigIntegerField(unique=True)

    def __str__(self):
        return f"{self.user.username} - {self.chat_id}"
