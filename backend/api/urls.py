from django.urls import path
from .views import GenerateBPMNView, UploadFileView

urlpatterns = [
    path('generate-bpmn/', GenerateBPMNView.as_view(), name='generate-bpmn'),
    path('upload-file/', UploadFileView.as_view(), name='upload-file'),
]
