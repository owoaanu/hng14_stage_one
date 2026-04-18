import requests
from django.utils import timezone
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet


from .models import Profile
from .serializers import ProfileSerializer

# External API Endpoints
GENDERIZE_URL = "https://api.genderize.io"
AGIFY_URL = "https://api.agify.io"
NATIONALIZE_URL = "https://api.nationalize.io"


def call_genderize(name):
    try:
        response = requests.get(f"{GENDERIZE_URL}?name={name}")
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        if data.get("gender") is None or data.get("count", 0) == 0:
            return None  # Indicate invalid response as per requirements
        return {
            "gender": data.get("gender"),
            "gender_probability": data.get("probability", 0.0),
            "sample_size": data.get("count"),
        }
    except requests.exceptions.RequestException as e:
        print(f"Error calling Genderize API: {e}")
        return None


def call_agify(name):
    try:
        response = requests.get(f"{AGIFY_URL}?name={name}")
        response.raise_for_status()
        data = response.json()
        if data.get("age") is None:
            return None  # Indicate invalid response
        return {"age": data.get("age")}
    except requests.exceptions.RequestException as e:
        print(f"Error calling Agify API: {e}")
        return None


def call_nationalize(name):
    try:
        response = requests.get(f"{NATIONALIZE_URL}?name={name}")
        response.raise_for_status()
        data = response.json()
        if not data.get("country"):
            return None  # Indicate invalid response

        # Find country with highest probability
        country_data = sorted(
            data["country"], key=lambda x: x.get("probability", 0), reverse=True
        )
        if country_data:
            return {
                "country_id": country_data[0].get("country_id"),
                "country_probability": country_data[0].get("probability", 0.0),
            }
        return (
            None  # Should not happen if data['country'] is not empty, but for safety.
        )
    except requests.exceptions.RequestException as e:
        print(f"Error calling Nationalize API: {e}")
        return None

def classify_age_group(age):
    """Classifies an age into an age group."""
    if age is None:
        return None
    if 0 <= age <= 12:
        return "child"
    elif 13 <= age <= 19:
        return "teenager"
    elif 20 <= age <= 59:
        return "adult"
    elif age >= 60:
        return "senior"
    return None




class ProfileViewSet(ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    lookup_field = "id" 
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ('name', 'gender', 'country_id', 'age_group') 
    ordering_fields = ('created_at', 'name', 'age', 'gender')

    def get_queryset(self):
        # Apply filtering based on query parameters
        queryset = super().get_queryset()
        gender = self.request.query_params.get("gender")
        country_id = self.request.query_params.get("country_id")
        age_group = self.request.query_params.get("age_group")

        if gender:
            queryset = queryset.filter(gender__iexact=gender)
        if country_id:
            queryset = queryset.filter(
                country_id__iexact=country_id
            ) 
        if age_group:
            queryset = queryset.filter(age_group__iexact=age_group) 

        return queryset

    def create(self, request, *args, **kwargs):
        name = request.data.get("name")
        if not name:
            return Response(
                {"status": "error", "message": "Name is required"}, status=400
            )

        name = name.strip()

        try:
            existing_profile = Profile.objects.get(name__iexact=name)
            serializer = self.get_serializer(existing_profile)
            return Response(
                {
                    "status": "success",
                    "message": "Profile already exists",
                    "data": serializer.data,
                },
                status=200,
            )
        except Profile.DoesNotExist:
            pass  

        # Call external APIs
        gender_data = call_genderize(name)
        age_data = call_agify(name)
        country_data = call_nationalize(name)

        if gender_data is None or age_data is None or country_data is None:
            error_message = ""
            if gender_data is None:
                error_message = "Genderize returned an invalid response"
            elif age_data is None:
                error_message = "Agify returned an invalid response"
            elif country_data is None:
                error_message = "Nationalize returned an invalid response"

            return Response(
                {"status": "502", "message": error_message},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        age = age_data.get("age")
        age_group = classify_age_group(age)

        profile_data = {
            "name": name,
            "gender": gender_data.get("gender"),
            "gender_probability": gender_data.get("gender_probability"),
            "sample_size": gender_data.get("sample_size"),
            "age": age,
            "age_group": age_group,
            "country_id": country_data.get("country_id"),
            "country_probability": country_data.get("country_probability"),
        }

        try:
            serializer = self.get_serializer(data=profile_data)
            serializer.is_valid(raise_exception=True)
            profile = serializer.save()

            response_data = {"status": "success", "data": serializer.data}
            return Response(response_data, status=200)

        except Exception as e:
            print(f"Error creating profile: {e}")
            return Response(
                {
                    "status": "error",
                    "message": "Failed to create profile due to a server error.",
                },
                status=500,
            )

    def retrieve(self, request, *args, **kwargs):
        # Fetch profile by ID
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        response_data = {"status": "success", "data": serializer.data}
        return Response(response_data, status=200)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # queryset = self.filter_queryset(self.queryset)
        

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        response_data = {
            "status": "success",
            "count": len(serializer.data),
            "data": serializer.data,
        }
        return Response(response_data, status=200)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=204)
