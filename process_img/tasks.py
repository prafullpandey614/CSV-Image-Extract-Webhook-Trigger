from celery import shared_task
from PIL import Image
import os
import requests
from io import BytesIO
from django.core.files.storage import default_storage
from django.conf import settings
from .models import Request, ProductImage

from django.conf import settings

def build_absolute_uri(relative_url):
    """
    Helper function to build an absolute URL.
    """
    return f"{settings.SITE_PROTOCOL}://{settings.SITE_DOMAIN}{relative_url}"

@shared_task
def process_images(request_id):
    try:
        # Fetch the request object from the database
        request_obj = Request.objects.get(request_id=request_id)
        request_obj.status = 'In Progress'
        request_obj.save()

        # Fetch all ProductImage entries associated with the request
        product_images = ProductImage.objects.filter(request=request_obj)

        # Process each product image entry
        for product in product_images:
            input_urls = product.input_image_urls.split(',')
            output_image_urls = []

            # Download, compress, and upload each image
            for url in input_urls:
                try:
                    # Download the image
                    response = requests.get(url.strip(), stream=True)
                    response.raise_for_status()

                    # Open the image using PIL
                    image = Image.open(BytesIO(response.content))

                    # Compress the image
                    compressed_image_io = BytesIO()
                    image.save(compressed_image_io, format=image.format, quality=50)
                    compressed_image_io.seek(0)

                    # Save or upload the compressed image
                    output_url = save_compressed_image(compressed_image_io, product.product_name, url)
                    output_image_urls.append(output_url)

                except Exception as e:
                    print(f"Failed to process image {url}: {e}")

            # Update product image entry with the output URLs
            product.output_image_urls = ','.join(output_image_urls)
            product.save()

        # Update the request status to 'Completed'
        request_obj.status = 'Completed'
        request_obj.save()
        if request_obj.webhook_url:
            trigger_webhook(request_obj)

    except Request.DoesNotExist:
        print(f"Request with ID {request_id} does not exist.")
    except Exception as e:
        print(f"An error occurred while processing images: {e}")
        # Optionally update request status to 'Failed' or log the error

def save_compressed_image(image_io, product_name, original_url):
    """
    Save or upload the compressed image and return its URL.
    """
    # Create a unique filename based on the original filename
    output_filename = f"{product_name}_{os.path.basename(original_url).split('.')[0]}_compressed.jpg"

    # Save the image file to the default storage (MEDIA_ROOT)
    file_path = os.path.join(settings.MEDIA_ROOT, output_filename)
    
    # Save the file using Django's default storage
    with default_storage.open(file_path, 'wb') as f:
        f.write(image_io.getvalue())

    # Generate the URL to access the file
    output_url = os.path.join(settings.MEDIA_URL, output_filename)
    # output_url = default_storage.url(file_path)
    
    return build_absolute_uri(output_url)

def trigger_webhook(request_obj):
    """
    Trigger a webhook by sending a POST request to the provided URL.
    """
    try:
        data = {
            'request_id': str(request_obj.request_id),
            'status': request_obj.status,
            'completed_at': request_obj.updated_at.isoformat(),
        }

        response = requests.post(request_obj.webhook_url, json=data)
        response.raise_for_status()  
        print(f"Webhook triggered successfully for request ID {request_obj.request_id}")

    except requests.exceptions.RequestException as e:
        print(f"Failed to trigger webhook for request ID {request_obj.request_id}: {e}")
        