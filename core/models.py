from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom user model to handle roles and additional fields.
    """
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
    # Roles
    is_admin = models.BooleanField(default=False)  # Super Admin control
    is_manager = models.BooleanField(default=False) # Organization/Workspace Manager
    
    def __str__(self):
        return self.username

class Organization(models.Model):
    """
    Represents a tenant or company account.
    """
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_organizations')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Membership(models.Model):
    """
    Link between User and Organization with roles within that org.
    """
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('member', 'Member'),
        ('viewer', 'Viewer'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'organization')

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.title}"

class FooterLink(models.Model):
    """
    Dynamic footer links controllable via Admin.
    """
    SECTION_CHOICES = (
        ('products', 'Products'),
        ('solutions', 'Solutions'),
        ('resources', 'Resources'),
        ('company', 'Company'),
    )
    title = models.CharField(max_length=100)
    url = models.CharField(max_length=200, help_text="URL or path (e.g., /pricing/ or https://google.com)")
    section = models.CharField(max_length=20, choices=SECTION_CHOICES)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['section', 'order']

    def __str__(self):
        return f"{self.get_section_display()} - {self.title}"
