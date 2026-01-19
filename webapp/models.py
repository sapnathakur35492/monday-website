from django.db import models
from django.conf import settings
from core.models import Organization

class Workspace(models.Model):
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='workspaces')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Board(models.Model):
    TYPE_CHOICES = (
        ('table', 'Table'),
        ('kanban', 'Kanban'),
        ('calendar', 'Calendar'),
    )
    PRIVACY_CHOICES = (
        ('private', 'Private'),
        ('team', 'Team'),
        ('public', 'Public'),
    )
    
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='boards')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='table')
    privacy = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default='team')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Group(models.Model):
    """
    A group of items within a board (e.g. 'This Week', 'Next Week').
    """
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='groups')
    title = models.CharField(max_length=255)
    color = models.CharField(max_length=20, default='#000000') # Increased length for rgba or names
    position = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['position']

    def __str__(self):
        return self.title

class Column(models.Model):
    """
    Definition of a column in a board.
    """
    COLUMN_TYPES = (
        ('text', 'Text'),
        ('status', 'Status'),
        ('date', 'Date'),
        ('person', 'People'),
        ('number', 'Numbers'),
        ('dropdown', 'Dropdown'),
        ('priority', 'Priority'),
        ('checkbox', 'Checkbox'),
        ('file', 'File'),
        ('formula', 'Formula'),
    )
    
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='columns')
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=COLUMN_TYPES)
    settings = models.JSONField(default=dict, blank=True) # Choices, Formula definition, etc.
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['position']

    def __str__(self):
        return self.title

class Item(models.Model):
    """
    A single row/task.
    """
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Store dynamic column values here. Key = column_id (str), Value = data.
    values = models.JSONField(default=dict, blank=True)
    
    position = models.PositiveIntegerField(default=0)

    # Attachments can be stored in a separate model or JSON if using external storage
    # For now, let's keep it simple or add an Attachment model later.

    class Meta:
        ordering = ['position']

    def __str__(self):
        return self.name

class ItemUpdate(models.Model):
    """
    Updates/Comments on an item (The 'Pulse').
    """
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='updates')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Optional: Liked by functionality for 'Monday' feel
    liked_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_updates', blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} on {self.item.name}"
