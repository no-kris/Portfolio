from django.db import models


class Project(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    technology = models.CharField(max_length=100)
    url = models.URLField(null=True)
    github_link = models.URLField(null=True)
    image = models.FileField(upload_to="project_images/", blank=True)
