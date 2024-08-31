import csv
import uuid
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import CSVUploadSerializer
from .models import Request, ProductImage
from .tasks import process_images

class CSVUploadView(APIView):
    """
    A generic view to handle the CSV file upload.
    """
    def post(self, request, *args, **kwargs):
        serializer = CSVUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        request_id = uuid.uuid4()
        webhook_url = request.data.get('webhook_url','')
        csv_request = Request.objects.create(request_id=request_id, status='Pending',webhook_url=webhook_url)

        csv_file = serializer.validated_data['file']
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        csv_reader = csv.reader(decoded_file)

        next(csv_reader, None)

        try:
            for row in csv_reader:
                serial_number = row[0].strip()
                product_name = row[1].strip()
                input_image_urls = row[2].strip()

                ProductImage.objects.create(
                    serial_number=serial_number,
                    product_name=product_name,
                    input_image_urls=input_image_urls,
                    request=csv_request
                )
        except Exception as e:
            csv_request.delete()
            return Response({"error": f"Invalid CSV format or data. Details: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        process_images.delay(str(request_id))

        return Response({"request_id": str(request_id)}, status=status.HTTP_201_CREATED)

class CheckStatus(APIView):
    def get(self,request,request_id):
        obj = get_object_or_404(Request,request_id=request_id)
        return Response({'status' : obj.status},status=status.HTTP_200_OK)
    
class DownloadOutPutCSV(APIView):
    """
    A view to download the output CSV with an additional column of output image URLs.
    """
    def get(self, request, request_id):
        try:
            request_obj = Request.objects.get(request_id=request_id)

            product_images = ProductImage.objects.filter(request=request_obj)

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="output_{request_id}.csv"'

            writer = csv.writer(response)

            writer.writerow(['S. No.', 'Product Name', 'Input Image URLs', 'Output Image URLs'])

            for product in product_images:
                writer.writerow([
                    product.serial_number,
                    product.product_name,
                    product.input_image_urls,
                    product.output_image_urls
                ])

            return response

        except Request.DoesNotExist:
            return Response({"error": "Request with the specified ID does not exist."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)