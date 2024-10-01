from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.urls import reverse

class Product(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.code} - {self.name}"

class ProductMedia(models.Model):
    product = models.ForeignKey(Product, related_name='media', on_delete=models.CASCADE)
    file = models.FileField(
        upload_to='product_media/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'mp4', 'mov'])]
    )
    duration = models.PositiveIntegerField(default=15, blank=True, help_text="Duration in seconds (for videos)")

    def __str__(self):
        return f"{self.product.code} - {self.file.name}"

class Station(models.Model):
    name = models.CharField(max_length=100)
    products = models.ManyToManyField(Product, related_name='stations',blank=True)
    manager = models.ForeignKey(User, on_delete=models.CASCADE,blank=True)
    selected_media = models.ManyToManyField(ProductMedia, related_name='stations', blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('station_detail', kwargs={'pk': self.pk})