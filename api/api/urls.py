from django.contrib import admin
from django.urls import path
from customer.api import RegisterCustomer
from loan.api import CheckEligibility, ViewLoanByLoanId,ViewLoansByCustomerId,CreateLoan

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register', RegisterCustomer.as_view(),name='register'),#Done
    path('check-eligibility', CheckEligibility.as_view(),name='check_eligibility'),#Left
    path('create-loan', CreateLoan.as_view(),name='create_loan'),#Left
    path('view-loan/<int:loan_id>', ViewLoanByLoanId.as_view(),name='view_loan_by_loan_id'), #Done
    path('view-loans/<int:customer_id>', ViewLoansByCustomerId.as_view(),name='view_loan_by_customer_id'),#Done
]