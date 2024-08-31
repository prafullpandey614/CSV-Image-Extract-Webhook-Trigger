from django.db import models

class Request(models.Model):
    request_id = models.UUIDField(unique=True)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('In Progress', 'In Progress'), ('Completed', 'Completed')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    webhook_url = models.URLField(null=True, blank=True)

class ProductImage(models.Model):
    serial_number = models.IntegerField()
    product_name = models.CharField(max_length=255)
    input_image_urls = models.TextField()
    output_image_urls = models.TextField(null=True, blank=True)
    request = models.ForeignKey(Request, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
