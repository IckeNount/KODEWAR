from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import CodeSubmissionSerializer, SubmissionResponseSerializer, StatusResponseSerializer
from .tasks import run_code_task
from celery.result import AsyncResult
import uuid
from django.core.cache import cache

# Create your views here.

def hello_world(request):
    return JsonResponse({"message": "Hello from Django!"})

class CodeSubmissionView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Handle code submission."""
        serializer = CodeSubmissionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        # Generate submission ID
        submission_id = uuid.uuid4()
        
        # Store submission in cache
        cache.set(
            f'submission_{submission_id}',
            {
                'status': 'pending',
                'data': serializer.validated_data
            },
            timeout=300  # 5 minutes
        )
        
        # Queue task
        run_code_task.delay(
            code=serializer.validated_data['code'],
            language=serializer.validated_data['language'],
            test_cases=serializer.validated_data.get('test_cases', []),
            submission_id=str(submission_id)
        )
        
        # Return response
        response_serializer = SubmissionResponseSerializer({
            'submission_id': submission_id,
            'status': 'pending'
        })
        return Response(response_serializer.data, status=status.HTTP_202_ACCEPTED)

class SubmissionStatusView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get submission status."""
        submission_id = request.query_params.get('submission_id')
        if not submission_id:
            return Response(
                {'error': 'submission_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Get submission from cache
        submission = cache.get(f'submission_{submission_id}')
        if not submission:
            return Response(
                {'error': 'Submission not found'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        # Return status
        response_serializer = StatusResponseSerializer(submission)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

class TaskStatusView(APIView):
    """
    API endpoint for checking task status.
    """
    # permission_classes = [IsAuthenticated]  # Temporarily disabled for testing
    
    def get(self, request, task_id, *args, **kwargs):
        """
        Get the status of a task.
        
        Args:
            task_id: The ID of the task to check
        """
        task_result = AsyncResult(task_id)
        
        if task_result.ready():
            if task_result.successful():
                return Response({
                    "status": "completed",
                    "result": task_result.result
                })
            else:
                return Response({
                    "status": "failed",
                    "error": str(task_result.result)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({
                "status": "pending",
                "task_id": task_id
            })
