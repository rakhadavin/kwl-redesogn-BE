from django.db import models

# Create your models here.
class Course(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    # Add other fields as needed

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title
