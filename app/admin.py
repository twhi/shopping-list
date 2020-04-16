from django.contrib import admin
from .models import List, Item

@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    pass

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    pass
