from rest_framework import serializers
from django.contrib.auth.models import User
from .models import TrackedTime

class TrackedTimeSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    user_id = serializers.ReadOnlyField(source='user.id')
    class Meta:
        model = TrackedTime
        fields = ['id', 'year', 'month', 'day', 'apps', 'user', 'user_id']