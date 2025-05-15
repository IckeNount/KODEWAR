from django.urls import path
from .views import CodeSubmissionView, TaskStatusView, hello_world

urlpatterns = [
    path('hello/', hello_world, name='hello_world'),
    path('api/submit/', CodeSubmissionView.as_view(), name='code_submission'),
    path('api/task/<str:task_id>/', TaskStatusView.as_view(), name='task_status'),
] 