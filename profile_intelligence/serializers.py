from rest_framework import serializers

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    # Explicitly define country_probability as optional if it can be null
    country_probability = serializers.FloatField(required=False, allow_null=True)

    class Meta:
        model = Profile
        fields = [
            "id",
            "name",
            "gender",
            "gender_probability",
            "sample_size",
            "age",
            "age_group",
            "country_id",
            "country_probability",
            "created_at",
        ]
        # Make id read-only as it's generated
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        new_profile = Profile(
            name = validated_data["name"],
            gender = validated_data["gender"],
            gender_probability = validated_data["gender_probability"],
            sample_size = validated_data["sample_size"],
            age = validated_data["age"],
            age_group = validated_data["age_group"],
            country_id = validated_data["country_id"],
            country_probability = validated_data["country_probability"]
        )
        
        new_profile.save()
        return new_profile

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr not in ["id", "created_at"]:
                setattr(instance, attr, value)
        instance.save()
        return instance
