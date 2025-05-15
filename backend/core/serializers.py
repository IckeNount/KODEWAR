from rest_framework import serializers

class CodeSubmissionSerializer(serializers.Serializer):
    code = serializers.CharField(
        required=True,
        min_length=1,
        max_length=50000,  # Reasonable limit for code submissions
        help_text="The code to be executed"
    )
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