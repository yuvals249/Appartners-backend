from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Apartment
from .serializers import ApartmentSerializer

class ApartmentListCreateView(APIView):
    """
    API View to list all apartments or create a new apartment.
    """
    def get(self, request):
        apartments = Apartment.objects.all()
        serializer = ApartmentSerializer(apartments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ApartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)