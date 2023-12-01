from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


def file_generate_upload_path(instance, filename):
	# Both filename and instance.file_name should have the same values
    return f"files/{instance.file_name}"


class Image(models.Model):
    image = models.FileField(
        upload_to=file_generate_upload_path,
        blank=True,
        null=True
    )

    original_image_name = models.TextField()

    image_name = models.CharField(max_length=255, unique=True)
    image_type = models.CharField(max_length=255)

    upload_finished_at = models.DateTimeField(blank=True, null=True)

    @property
    def is_valid(self):
        """
        We consider a image "valid" if the the datetime flag has value.
        """
        return bool(self.upload_finished_at)

    @property
    def url(self):
        if settings.FILE_UPLOAD_STORAGE == "s3":
            return self.image.url

        return f"{settings.APP_DOMAIN}{self.file.url}"