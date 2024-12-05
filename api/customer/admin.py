from django.contrib import admin
from .models import Customer

# Register your models here.

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_id', 'first_name', 'last_name', 'age', 'phone_number', 'monthly_salary', 'approved_limit')
    search_fields = ('customer_id','first_name', 'last_name', 'phone_number')
    list_filter = ('age',)