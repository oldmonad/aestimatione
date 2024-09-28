from django.urls import path
from .views.reconcilation import FileUploadView

app_name = "reconcilation"

urlpatterns = [
    path("uploads/", FileUploadView.as_view(), name='upload'),
]
