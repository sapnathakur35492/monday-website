from django.contrib import admin
from .models import Workspace, Board, Group, Column, Item

class ColumnInline(admin.TabularInline):
    model = Column
    extra = 0

class GroupInline(admin.StackedInline):
    model = Group
    extra = 0

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('name', 'workspace', 'created_by')
    inlines = [ColumnInline, GroupInline]

admin.site.register(Workspace)
admin.site.register(Item)
