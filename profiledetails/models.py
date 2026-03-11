from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Projects(models.Model):
    project_title = models.CharField(max_length=200)
    project_series = models.CharField(max_length=200)
    project_technology = models.TextField()
    project_desc = models.TextField()
    project_link = models.URLField(max_length=200, blank=True, help_text="Project link (if any)")
    
    def __str__(self):
        return self.project_title
    
    class Meta:
        verbose_name_plural = "Projects"

class contactus(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(max_length=254)
    phone = models.CharField(max_length=50)
    desc = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.name} - {self.email}" 
    
    class Meta:
        verbose_name_plural = "Contact Messages"
        ordering = ['-created_at']

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True, help_text="Upload your resume (PDF)")

    def __str__(self):
        return self.user.email
    
    class Meta:
        verbose_name_plural = "User Profiles"