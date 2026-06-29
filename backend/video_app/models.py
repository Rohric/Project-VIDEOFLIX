from django.db import models
from django.utils import timezone


class Video(models.Model):
    CATEGORY_CHOICES = [
        ("Drama", "Drama"),
        ("Romance", "Romance"),
        ("Action", "Action"),
        ("Comedy", "Comedy"),
        ("Horror", "Horror"),
        ("Thriller", "Thriller"),
    ]

    created_at = models.DateTimeField(default=timezone.now)
    title = models.CharField(max_length=255)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to="thumbnails/")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    video_file = models.FileField(upload_to="videos/")

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]


class VideoFileInfo(models.Model):
    RESOLUTION_CHOICES = [
        ("480p", "480p"),
        ("720p", "720p"),
        ("1080p", "1080p"),
    ]
    STATUS_CHOICES = [
        ("waiting", "Waiting"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="waiting")

    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="file_infos")
    resolution = models.CharField(max_length=10, choices=RESOLUTION_CHOICES)
    manifest_file = models.FileField(upload_to="hls/manifests/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.video.title} - {self.resolution}"

    class Meta:
        unique_together = ("video", "resolution")
