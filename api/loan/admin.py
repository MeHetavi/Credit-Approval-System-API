from django.contrib import admin
from .models import Loan

# Register your models here.

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('loan_id', 'customer', 'loan_amount', 'tenure', 'interest_rate', 'monthly_installment', 'emi_paid_on_time', 'start_date', 'end_date')
    search_fields = ('customer__first_name', 'customer__last_name', 'loan_id')
    list_filter = ('start_date', 'end_date', 'interest_rate')