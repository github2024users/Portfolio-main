from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.files.storage import default_storage
from django.conf import settings
from django.http import FileResponse
from .serializers import UserSerializer
from .models import UserProfile, Projects, contactus
import json
import os
import traceback



# ============= REGISTER API =============
class RegisterAPIView(APIView):
    def post(self, request):
        try:
            # REST Framework automatically parses JSON to request.data
            data = request.data if hasattr(request, 'data') else request.POST
            
            if not all([data.get('username'), data.get('email'), data.get('first_name'), 
                       data.get('password'), data.get('confirm_password')]):
                return Response(
                    {"error": "Please fill all required fields!"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if data.get('password') != data.get('confirm_password'):
                return Response(
                    {"error": "Passwords do not match!"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if len(data.get('password', '')) < 6:
                return Response(
                    {"error": "Password must be at least 6 characters long!"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if User.objects.filter(username=data.get('username')).exists():
                return Response(
                    {"error": "Username already exists!"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if User.objects.filter(email=data.get('email')).exists():
                return Response(
                    {"error": "Email already registered!"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user = User.objects.create_user(
                username=data.get('username'),
                email=data.get('email'),
                password=data.get('password'),
                first_name=data.get('first_name')
            )
            
            phone = data.get('phone', '')
            bio = data.get('bio', '')
            
            UserProfile.objects.create(
                user=user,
                phone=phone,
                bio=bio
            )
            
            return Response(
                {
                    "message": "Registration successful! Please login now.",
                    "success": True
                },
                status=status.HTTP_201_CREATED
            )
        
        except Exception as e:
            traceback.print_exc()
            return Response(
                {"error": f"Registration failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============= LOGIN API =============
class LoginAPIView(APIView):
    def post(self, request):
        try:
            # REST Framework automatically parses JSON to request.data
            email = request.data.get('email') if hasattr(request, 'data') else request.POST.get('email')
            password = request.data.get('password') if hasattr(request, 'data') else request.POST.get('password')
            
            if not email or not password:
                return Response(
                    {"error": "Email and password are required!"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                user_obj = User.objects.get(email=email)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                return Response(
                    {"error": "Invalid email or password!"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if user is not None:
                login(request, user)
                return Response({
                    "message": f"Welcome back, {user.first_name or user.username}!",
                    "success": True,
                    "user_id": user.id,
                    "username": user.username,
                    "email": user.email
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "Invalid email or password!"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        except Exception as e:
            traceback.print_exc()
            return Response(
                {"error": f"Login failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============= LOGOUT API =============
class LogoutAPIView(APIView):
    def post(self, request):
        try:
            logout(request)
            return Response(
                {
                    "message": "Logged out successfully!",
                    "success": True
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": f"Logout failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============= GET RESUME API =============
class GetResumeAPIView(APIView):
    """Get user's resume URL"""
    def get(self, request):
        try:
            # Check if user is authenticated
            if request.user.is_authenticated:
                try:
                    profile = request.user.profile
                    if profile.resume and profile.resume.name:
                        # Build the full media URL
                        resume_url = f"{request.build_absolute_uri('/media/')}{profile.resume.name}"
                        filename = profile.resume.name.split('/')[-1]
                        
                        return Response({
                            "success": True,
                            "resume_url": resume_url,
                            "filename": filename,
                            "is_uploaded": True
                        }, status=status.HTTP_200_OK)
                    else:
                        # No resume uploaded yet
                        return Response({
                            "success": True,
                            "resume_url": None,
                            "filename": None,
                            "is_uploaded": False,
                            "message": "No resume uploaded yet"
                        }, status=status.HTTP_200_OK)
                except UserProfile.DoesNotExist:
                    # Profile doesn't exist
                    return Response({
                        "success": True,
                        "resume_url": None,
                        "filename": None,
                        "is_uploaded": False,
                        "message": "User profile not found"
                    }, status=status.HTTP_200_OK)
            else:
                # Not authenticated
                return Response({
                    "success": True,
                    "resume_url": None,
                    "filename": None,
                    "is_uploaded": False,
                    "message": "User not authenticated"
                }, status=status.HTTP_200_OK)
        
        except Exception as e:
            traceback.print_exc()
            return Response({
                "success": False,
                "error": f"Failed to fetch resume: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============= DOWNLOAD RESUME API (Alternative Direct Download) =============
class DownloadResumeAPIView(APIView):
    """Download user's resume file directly"""
    def get(self, request):
        try:
            if request.user.is_authenticated:
                try:
                    profile = request.user.profile
                    if profile.resume and profile.resume.name:
                        # Open and return the file
                        response = FileResponse(profile.resume.open('rb'), as_attachment=True)
                        filename = profile.resume.name.split("/")[-1]
                        response['Content-Disposition'] = f'attachment; filename="{filename}"'
                        response['Content-Type'] = 'application/pdf'
                        return response
                    else:
                        return Response({
                            "error": "No resume uploaded yet"
                        }, status=status.HTTP_404_NOT_FOUND)
                except UserProfile.DoesNotExist:
                    return Response({
                        "error": "User profile not found"
                    }, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({
                    "error": "User not authenticated"
                }, status=status.HTTP_401_UNAUTHORIZED)
        
        except Exception as e:
            traceback.print_exc()
            return Response({
                "error": f"Failed to download resume: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============= RESUME UPLOAD API =============
class UploadResumeAPIView(APIView):
    """Upload or update user's resume"""
    @method_decorator(login_required(login_url='login'))
    def post(self, request):
        try:
            if 'resume' not in request.FILES:
                return Response(
                    {"error": "No file provided!"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            resume_file = request.FILES['resume']
            
            # Validate file type
            if not resume_file.name.endswith('.pdf'):
                return Response(
                    {"error": "Only PDF files are allowed!"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate file size (max 5MB)
            max_size = 5 * 1024 * 1024
            if resume_file.size > max_size:
                return Response(
                    {"error": "File size must be less than 5MB!"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create resume directory if it doesn't exist
            resume_dir = os.path.join(settings.MEDIA_ROOT, 'resumes')
            os.makedirs(resume_dir, exist_ok=True)
            
            # Save resume with user-specific naming
            filename = f'{request.user.username}_resume.pdf'
            filepath = os.path.join(resume_dir, filename)
            
            # Delete old resume if exists
            if os.path.exists(filepath):
                os.remove(filepath)
            
            # Save new resume
            with open(filepath, 'wb+') as destination:
                for chunk in resume_file.chunks():
                    destination.write(chunk)
            
            # Store resume path in UserProfile
            try:
                profile = request.user.profile
                profile.resume = f'resumes/{filename}'
                profile.save()
            except UserProfile.DoesNotExist:
                UserProfile.objects.create(
                    user=request.user,
                    resume=f'resumes/{filename}'
                )
            
            return Response({
                "success": True,
                "message": "Resume uploaded successfully!",
                "filename": filename
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            traceback.print_exc()
            return Response(
                {"error": f"Failed to upload resume: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============= GET MESSAGES API (NEW) =============
class GetMessagesAPIView(APIView):
    """Get all contact messages"""
    @method_decorator(login_required(login_url='login'))
    def get(self, request):
        try:
            messages = contactus.objects.all().values(
                'id', 'name', 'email', 'phone', 'desc', 'created_at'
            ).order_by('-created_at')
            
            messages_list = list(messages)
            
            return Response({
                "success": True,
                "messages": messages_list
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            traceback.print_exc()
            return Response(
                {"error": f"Failed to load messages: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============= DELETE MESSAGE API (NEW) =============
class DeleteMessageAPIView(APIView):
    """Delete a contact message"""
    @method_decorator(login_required(login_url='login'))
    def delete(self, request, id):
        try:
            message = contactus.objects.get(id=id)
            message.delete()
            
            return Response({
                "success": True,
                "message": "Message deleted successfully!"
            }, status=status.HTTP_200_OK)
        
        except contactus.DoesNotExist:
            return Response(
                {"error": "Message not found!"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            traceback.print_exc()
            return Response(
                {"error": f"Failed to delete message: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============= PROJECTS DASHBOARD API =============
@method_decorator(login_required(login_url='login'), name='dispatch')
class ProjectsAPIView(APIView):
    """Get all projects"""
    def get(self, request):
        try:
            projects = Projects.objects.all().values(
                'id', 'project_title', 'project_series', 'project_technology', 
                'project_desc', 'project_link'
            )
            
            # Add created_at field (using id as proxy since Projects doesn't have it)
            projects_list = []
            for project in projects:
                project['created_at'] = '2024-01-01'  # Default date
                projects_list.append(project)
            
            return Response({
                "success": True,
                "projects": projects_list
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            traceback.print_exc()
            return Response(
                {"error": f"Failed to load projects: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(login_required(login_url='login'), name='dispatch')
class AddProjectAPIView(APIView):
    """Add new project"""
    def post(self, request):
        try:
            project_title = request.POST.get('project_title')
            project_series = request.POST.get('project_series')
            project_technology = request.POST.get('project_technology')
            project_desc = request.POST.get('project_desc')
            project_link = request.POST.get('project_link', '')
            
            if not all([project_title, project_series, project_technology, project_desc]):
                return Response(
                    {"error": "Please fill all required fields!"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            project = Projects.objects.create(
                project_title=project_title,
                project_series=project_series,
                project_technology=project_technology,
                project_desc=project_desc,
                project_link=project_link
            )
            
            return Response({
                "success": True,
                "message": "Project added successfully!",
                "id": project.id
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            traceback.print_exc()
            return Response(
                {"error": f"Failed to add project: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(login_required(login_url='login'), name='dispatch')
class DeleteProjectAPIView(APIView):
    """Delete project"""
    def delete(self, request, id):
        try:
            project = Projects.objects.get(id=id)
            project.delete()
            
            return Response({
                "success": True,
                "message": "Project deleted successfully!"
            }, status=status.HTTP_200_OK)
        
        except Projects.DoesNotExist:
            return Response(
                {"error": "Project not found!"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            traceback.print_exc()
            return Response(
                {"error": f"Failed to delete project: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(login_required(login_url='login'), name='dispatch')
class UpdateProjectAPIView(APIView):
    """Update existing project"""
    def put(self, request, id):
        try:
            project = Projects.objects.get(id=id)
            
            project_title = request.POST.get('project_title')
            project_series = request.POST.get('project_series')
            project_technology = request.POST.get('project_technology')
            project_desc = request.POST.get('project_desc')
            project_link = request.POST.get('project_link', '')
            
            if not all([project_title, project_series, project_technology, project_desc]):
                return Response(
                    {"error": "Please fill all required fields!"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update project
            project.project_title = project_title
            project.project_series = project_series
            project.project_technology = project_technology
            project.project_desc = project_desc
            project.project_link = project_link
            project.save()
            
            return Response({
                "success": True,
                "message": "Project updated successfully!",
                "id": project.id
            }, status=status.HTTP_200_OK)
        
        except Projects.DoesNotExist:
            return Response(
                {"error": "Project not found!"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            traceback.print_exc()
            return Response(
                {"error": f"Failed to update project: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )