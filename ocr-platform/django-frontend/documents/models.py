from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os


def doc_upload_path(instance, filename):
    return f'docs/{timezone.now().strftime("%Y/%m/%d")}/{filename}'


class Doc(models.Model):
    file_path = models.FileField(upload_to=doc_upload_path)
    size = models.FloatField(help_text="Size in KB")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return os.path.basename(self.file_path.name)

    def save(self, *args, **kwargs):
        # Calculate file size in KB
        if not self.pk:  # Only for new files
            self.size = self.file_path.size / 1024
        super().save(*args, **kwargs)


class UserToDoc(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    doc = models.ForeignKey(Doc, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'doc')

    def __str__(self):
        return f"{self.user.username} - {self.doc}"


class FileType(models.Model):
    EXTENSION_CHOICES = [
        ('.jpg', 'JPEG Image'),
        ('.jpeg', 'JPEG Image'),
        ('.png', 'PNG Image'),
        ('.pdf', 'PDF Document'),
        ('.tiff', 'TIFF Image'),
    ]

    extension = models.CharField(
        max_length=10,
        choices=EXTENSION_CHOICES,
        unique=True
    )
    price = models.FloatField(help_text="Price per KB")

    def __str__(self):
        return f"{self.extension} (${self.price}/KB)"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    doc = models.ForeignKey(Doc, on_delete=models.CASCADE)
    order_price = models.FloatField()
    payment = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart #{self.id} - {self.user.username} - ${self.order_price}"

    def save(self, *args, **kwargs):
        # Calculate order price: size * price per KB
        if not self.pk:
            file_type = FileType.objects.filter(
                extension=os.path.splitext(self.doc.file_path.name)[1].lower()
            ).first()

            if file_type:
                self.order_price = self.doc.size * file_type.price
            else:
                self.order_price = 0
        super().save(*args, **kwargs)