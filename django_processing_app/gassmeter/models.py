from django.db import models


# Create your models here.
class Gassmeter(models.Model):

    timestamp = models.DateTimeField()  # Time of image capture
    text = models.CharField(max_length=100)  # Recognised value
    image_hash = models.CharField(max_length=64, unique=True, null=True)  # Hash of the image

    value = models.FloatField()  # Dummy field

    def __str__(self):
        return f"{self.timestamp} - {self.text}- {self.value}"