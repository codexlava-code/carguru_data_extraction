from django.db import models

class Machine(models.Model):
    machine_name = models.CharField(max_length=50, unique=True)
    equipment_id = models.CharField(max_length=50, unique=True)
    company_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.machine_name
    
    class Meta:
        verbose_name = 'Machine'
        verbose_name_plural  = 'machines'

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return self.name
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural  = 'categories'

class Subcategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, unique=True)
    variable_name = models.CharField(max_length=50, unique=True)
    unit = models.CharField(max_length=50, null=True)
    mini_limit = models.FloatField(null=True)
    maxi_limit = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return self.name
    
    class Meta:
        verbose_name = 'Subcategory'
        verbose_name_plural  = 'subcategories'
        
    @property
    def count_category(self):
        ...
