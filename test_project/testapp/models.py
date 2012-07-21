from django.db import models
from adminfiles.models import FileUpload

class Article(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()

    image = models.ForeignKey(FileUpload, null=True)

    def __unicode__(self):
        return self.title
