from django.db import models

class Feature(models.Model):
    """
    Dynamic features for the Features page.
    """
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon_name = models.CharField(max_length=50, help_text="SVG icon identifier (e.g., 'boards', 'automation', 'team')")
    order = models.IntegerField(default=0, help_text="Display order (lower numbers first)")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order', 'id']
    
    def __str__(self):
        return self.title

class Page(models.Model):
    """
    Admin-editable pages for the Marketing Website.
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField(help_text="HTML Content for the page body")
    meta_description = models.CharField(max_length=160, blank=True)
    is_published = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


