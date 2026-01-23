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
        ('gantt', 'Gantt Chart'),
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
        ('timeline', 'Timeline'),
        ('tags', 'Tags'),
        ('link', 'Link'),
        ('world_clock', 'World Clock'),
        ('item_id', 'Item ID'),
        ('phone', 'Phone'),
        ('location', 'Location'),
        ('rating', 'Rating'),
        ('progress', 'Progress'),
        ('email', 'Email'),
        ('vote', 'Vote'),
        ('creation_log', 'Creation Log'),
        ('last_updated', 'Last Updated'),
        ('auto_number', 'Auto Number'),
        ('country', 'Country'),
        ('color_picker', 'Color Picker'),
        ('time_tracking', 'Time Tracking'),
        ('week', 'Week'),
        ('hour', 'Hour'),
        ('dependency', 'Dependency'),
        ('connect_boards', 'Connect Boards'),
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
    # Subitems support: Parent item
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subitems')
    
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Store dynamic column values here. Key = column_id (str), Value = data.
    values = models.JSONField(default=dict, blank=True)
    
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['position']

    def __str__(self):
        return self.name

class ItemAttachment(models.Model):
    """
    Files attached to an item, often linked to a File column.
    """
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/%Y/%m/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    column_id = models.CharField(max_length=50, blank=True) # Optional: track which column this file belongs to

    def __str__(self):
        return self.file.name

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
        return f"Update by {self.user} on {self.item}"

class UserDashboard(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='dashboards', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class DashboardWidget(models.Model):
    WIDGET_TYPES = (
        ('numbers', 'Numbers'),
        ('chart', 'Chart'),
        ('battery', 'Battery'),
        ('text', 'Text'),
    )
    dashboard = models.ForeignKey(UserDashboard, on_delete=models.CASCADE, related_name='widgets')
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=WIDGET_TYPES)
    settings = models.JSONField(default=dict) # Source board_id, column_id, calculation type
    position = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['position']

    def __str__(self):
        return f"{self.title} ({self.type})"
