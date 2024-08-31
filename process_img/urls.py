from django.urls import path
from .views import CSVUploadView,CheckStatus,DownloadOutPutCSV
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('upload/', CSVUploadView.as_view(), name='csv-upload'),
    path('check-status/<str:request_id>/', CheckStatus.as_view(), name='check-status'),
    path('download-csv/<str:request_id>/', DownloadOutPutCSV.as_view(), name='csv-upload'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    