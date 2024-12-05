from rest_framework import serializers
from .models import Loan
      
class LoanByLoanIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ['loan_id','loan_amount','interest_rate','monthly_installment','tenure']

class LoanByCustomerIdSerializer(serializers.ModelSerializer):
    repayments_left = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = ['loan_id', 'loan_amount', 'interest_rate', 'monthly_installment', 'repayments_left']

    def get_repayments_left(self, obj):

        tenure = obj.tenure
        emi_paid = obj.emi_paid_on_time 
        return max(tenure - emi_paid, 0)