from django.db import models
from django.conf import settings

# Create your models here.
class Genre(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
class Film(models.Model):
    title = models.CharField(max_length=255)
    year = models.PositiveIntegerField()
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    
class History(models.Model):
    userid = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)
    filename = models.CharField(max_length=255)
    image = models.ImageField(upload_to='images/')
    timestamp = models.DateTimeField(auto_now_add=True)
    label = models.CharField(max_length=255)

    def __str__(self):
        return self.filename

