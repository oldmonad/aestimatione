from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers.reconcilation import FileSerializers
from django.http import HttpResponse
from ..utils import convert_to_csv, convert_to_html

class FileUploadView(APIView):
    serializer_class = FileSerializers

    def post(self, request):
      serializer = self.serializer_class(data=request.data, context={'request': request})
      if serializer.is_valid():
        format = request.data.get("format").lower()

        if format == "csv":
          response = HttpResponse(convert_to_csv(serializer.validated_data), content_type='text/csv')
          response['Content-Disposition'] = 'attachment; filename="reconciliation.csv"'
          return response
        elif format == "html":
          response = HttpResponse(convert_to_html(serializer.validated_data), content_type='text/html')
          response['Content-Disposition'] = 'attachment; filename="reconciliation.html"'
          return response
        else:
          return Response(serializer.validated_data, status=status.HTTP_200_OK)
      else:
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
