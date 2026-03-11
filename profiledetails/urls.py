from django.urls import path
from .views import (
    RegisterAPIView, LoginAPIView, LogoutAPIView,
    ProjectsAPIView, AddProjectAPIView, UpdateProjectAPIView, DeleteProjectAPIView,
    UploadResumeAPIView, GetResumeAPIView,
    GetMessagesAPIView, DeleteMessageAPIView
)

urlpatterns = [
    # Authentication endpoints
    path('api/register/', RegisterAPIView.as_view(), name='api-register'),
    path('api/login/', LoginAPIView.as_view(), name='api-login'),
    path('api/logout/', LogoutAPIView.as_view(), name='api-logout'),
    
    # Project endpoints
    path('api/projects/', ProjectsAPIView.as_view(), name='api-projects'),
    path('api/add-project/', AddProjectAPIView.as_view(), name='api-add-project'),
    path('api/update-project/<int:id>/', UpdateProjectAPIView.as_view(), name='api-update-project'),
    path('api/delete-project/<int:id>/', DeleteProjectAPIView.as_view(), name='api-delete-project'),
    
    # Resume endpoints
    path('api/upload-resume/', UploadResumeAPIView.as_view(), name='api-upload-resume'),
    path('api/get-resume/', GetResumeAPIView.as_view(), name='api-get-resume'),
    
    # Message endpoints (NEW)
    path('api/messages/', GetMessagesAPIView.as_view(), name='api-messages'),
    path('api/delete-message/<int:id>/', DeleteMessageAPIView.as_view(), name='api-delete-message'),
]