from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import CodeSubmissionSerializer
from .tasks import run_code_task
from celery.result import AsyncResult

# Create your views here.

def hello_world(request):
    return JsonResponse({"message": "Hello from Django!"})

class CodeSubmissionView(APIView):
    """
    API endpoint for submitting code for execution.
    """
    # permission_classes = [IsAuthenticated]  # Temporarily disabled for testing
    
    def post(self, request, *args, **kwargs):
        """
        Handle code submission.
        
        Expected JSON payload:
        {
            "code": "def solution(x): return x * 2",
            "test_file": "test_solution.py",
            "timeout": 30,
            "memory_limit": 512,
            "metadata": {
                "language": "python",
                "challenge_id": "123"
            }
        }
        """
        serializer = CodeSubmissionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    "status": "error",
                    "message": "Invalid submission data",
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Enqueue the task
        task = run_code_task.delay(
            code=serializer.validated_data['code'],
            test_file=serializer.validated_data['test_file'],
            timeout=serializer.validated_data['timeout'],
            memory_limit=serializer.validated_data['memory_limit']
        )
        
        return Response(
            {
                "status": "queued",
                "message": "Code submission received",
                "task_id": task.id,
                "metadata": serializer.validated_data.get('metadata', {})
            },
            status=status.HTTP_202_ACCEPTED
        )

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
