from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apartments.serializers import ApartmentSerializer


class ApartmentCreateView(APIView):
    """
    API View to create a new apartment.
    """

    def post(self, request):
        serializer = ApartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#
# # Retrieve, Update, and Delete a Single Apartment
# class ApartmentDetailView(APIView):
#     """
#     API View to retrieve, update, or delete a specific apartment.
#     """
#
#     def get(self, request, pk):
#         apartment = get_object_or_404(Apartment, pk=pk)
#         serializer = ApartmentSerializer(apartment)
#         return Response(serializer.data)
#
#     def put(self, request, pk):
#         apartment = get_object_or_404(Apartment, pk=pk)
#         serializer = ApartmentSerializer(apartment, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def delete(self, request, pk):
#         apartment = get_object_or_404(Apartment, pk=pk)
#         apartment.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
#
#
# # List and Create Features
# class FeatureListCreateView(APIView):
#     """
#     API View to list all features or create a new feature.
#     """
#
#     def get(self, request):
#         features = Feature.objects.all()
#         serializer = FeatureSerializer(features, many=True)
#         return Response(serializer.data)
#
#     def post(self, request):
#         serializer = FeatureSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# # Add Features to an Apartment
# class AddFeatureToApartmentView(APIView):
#     """
#     API View to add a feature to an apartment.
#     """
#
#     def post(self, request):
#         apartment_id = request.data.get('apartment_id')
#         feature_id = request.data.get('feature_id')
#
#         if not apartment_id or not feature_id:
#             return Response({"error": "apartment_id and feature_id are required"}, status=status.HTTP_400_BAD_REQUEST)
#
#         # Validate the Apartment and Feature exist
#         apartment = get_object_or_404(Apartment, pk=apartment_id)
#         feature = get_object_or_404(Feature, pk=feature_id)
#
#         # Create the relationship
#         ApartmentFeature.objects.create(apartment=apartment, feature=feature)
#         return Response({"message": "Feature added to apartment"}, status=status.HTTP_201_CREATED)
#
#
# # List Apartment Photos
# class ApartmentPhotoListView(APIView):
#     """
#     API View to list photos of an apartment.
#     """
#
#     def get(self, request, apartment_id):
#         photos = ApartmentPhoto.objects.filter(apartment__id=apartment_id)
#         serializer = ApartmentPhotoSerializer(photos, many=True)
#         return Response(serializer.data)
