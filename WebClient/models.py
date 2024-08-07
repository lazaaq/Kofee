from django.db import models
from django.conf import settings
from .helper import getImageFilenameTimestamp

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
    
def imageuploadfilename(instance, filename):
    file_name = getImageFilenameTimestamp(filename)
    return 'images/' + file_name

class Label(models.Model):
    name = models.CharField(max_length=255)
    treatment = models.TextField(default="Tidak dibutuhkan treatment khusus")

    def __str__(self):
        return self.name

class History(models.Model):
    userid = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)
    label = models.ForeignKey(Label, on_delete=models.CASCADE, default=2)
    filename = models.CharField(max_length=255, default="")
    image = models.ImageField(upload_to=imageuploadfilename)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.image

