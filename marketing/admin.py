from django.contrib import admin
from .models import Page, Feature, ComparisonItem

@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active')
    list_editable = ('order', 'is_active')


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'updated_at')
    prepopulated_fields = {'slug': ('title',)}



@admin.register(ComparisonItem)
class ComparisonItemAdmin(admin.ModelAdmin):
    list_display = ('feature_name', 'projectflow_text', 'monday_text', 'order', 'is_active')
    list_editable = ('order', 'is_active')
