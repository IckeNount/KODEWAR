from rest_framework import serializers
from .models import CodeSubmission

class TestCaseSerializer(serializers.Serializer):
    input = serializers.JSONField()
    expected = serializers.JSONField()

class CodeSubmissionSerializer(serializers.Serializer):
    code = serializers.CharField(
        required=True,
        min_length=1,
        max_length=50000,  # Reasonable limit for code submissions
        help_text="The code to be executed"
    )
    language = serializers.ChoiceField(choices=['python', 'javascript'])
    test_cases = TestCaseSerializer(many=True, required=False, default=list)
    test_file = serializers.CharField(
        required=True,
        help_text="Path to the test file"
    )
    timeout = serializers.IntegerField(
        required=False,
        default=30,
        min_value=1,
        max_value=300,  # 5 minutes max
        help_text="Test execution timeout in seconds"
    )
    memory_limit = serializers.IntegerField(
        required=False,
        default=512,
        min_value=128,
        max_value=2048,  # 2GB max
        help_text="Memory limit in MB"
    )
    metadata = serializers.JSONField(
        required=False,
        default=dict,
        help_text="Additional metadata about the submission"
    )

class SubmissionResponseSerializer(serializers.Serializer):
    submission_id = serializers.UUIDField()
    status = serializers.CharField()

class TestResultSerializer(serializers.Serializer):
    passed = serializers.BooleanField()
    input = serializers.JSONField()
    expected = serializers.JSONField()
    actual = serializers.JSONField()

class StatusResponseSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['pending', 'success', 'error'])
    output = serializers.CharField(required=False)
    error = serializers.CharField(required=False)
    test_results = TestResultSerializer(many=True, required=False) 