from rest_framework import serializers
from .models import StudentRisk

class StudentRiskSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentRisk
        fields = ['student', 'risk_level', 'confidence', 'last_updated']