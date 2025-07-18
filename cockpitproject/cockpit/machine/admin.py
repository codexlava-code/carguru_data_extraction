from django.contrib import admin

from .models import Machine, Category, Subcategory

class MachineAdmin(admin.ModelAdmin):
    search_fields = ['machine_name']

admin.site.register(Machine, MachineAdmin)

class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['name']

admin.site.register(Category, CategoryAdmin)

class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ['category','name', 'variable_name', 'unit']
    search_fields = ['category','name']
    list_filter = ['category']

admin.site.register(Subcategory, SubcategoryAdmin)

