from django.contrib import admin
from .models import Item

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('item_id', 'type', 'by', 'title', 'score', 'time', 'created_locally')
    list_filter = ('type', 'created_locally', 'dead')
    search_fields = ('item_id', 'by', 'title', 'text')
    readonly_fields = ('synced_at',)
    date_hierarchy = 'time'
    
    def get_readonly_fields(self, request, obj=None):
        """Make item_id readonly for existing objects"""
        if obj:
            return self.readonly_fields + ('item_id',)
        return self.readonly_fields