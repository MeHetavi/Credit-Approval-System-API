from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Loan
from customer.models import Customer
from .serializers import  LoanByLoanIdSerializer,LoanByCustomerIdSerializer
from dateutil.relativedelta import relativedelta


def is_loan_from_current_year(start_date, end_date):
    return start_date.year < datetime.now().year < end_date.year

def calculate_credit_score(customer_loans):
    try:
        past_loans_paid_on_time = len([loan for loan in customer_loans if loan.emi_paid_on_time == loan.tenure])
        total_loans = len(customer_loans)
        current_year_loans = len([loan for loan in customer_loans if is_loan_from_current_year(loan.start_date,loan.end_date)])
        total_loan_volume = sum(loan.loan_amount for loan in customer_loans)
        
        if total_loans:
            score =  (past_loans_paid_on_time / total_loans * 40 +  # Past loans paid on time
            (1 - (current_year_loans / total_loans)) * 20 +  # Loan activity
            (total_loan_volume / 100000) * 20 +  # Loan approved volume
            (1 - (total_loans / 10)) * 20  # Number of loans taken    
        )
        else:
            score = 100

        return min(max(score, 0), 100)  # Normalize between 0-100
    except Exception as e:
        return 0

def calculate_current_emis(customer):
    try:
        customer_loans = Loan.objects.filter(customer_id=customer.customer_id)
        return sum(loan.monthly_installment for loan in customer_loans)
    except Exception as e:
        return 0

def calculate_monthly_installment(loan_amount, interest_rate, tenure):
    try:
        monthly_rate = interest_rate / 12 / 100
        monthly_installment = loan_amount * (monthly_rate * (1 + monthly_rate)**tenure) / ((1 + monthly_rate)**tenure - 1)
        return round(monthly_installment, 2)
    except Exception as e:
        return 0

def check_loan_eligibility(customer, loan_request):
    try:
        # Check current total EMIs against monthly salary
        current_emis = calculate_current_emis(customer)

        if current_emis > (0.5 * customer.monthly_salary):
            return {
                'customer_id': customer.customer_id,
                'approval': False,
                'interest_rate': loan_request['interest_rate'],
                'corrected_interest_rate': None,
                'tenure': None,
                'monthly_installment': None,
                'Reason' : 'current_emis > (0.5 * monthly_salary)'
                }

        # Calculate credit score.
        customer_loans =  Loan.objects.filter(customer=customer)
        credit_score = calculate_credit_score(customer_loans)

        # Loan amount check against approved limit.
        total_current_loans = sum(loan.loan_amount for loan in Loan.objects.filter(
                                customer=customer, 
                                end_date__gt=datetime.now() # Still active loans
                            ))
        if (total_current_loans + loan_request['loan_amount']) > customer.approved_limit:
            credit_score = 0

        # Interest rate adjustment based on credit score.
        corrected_interest_rate = loan_request['interest_rate']
        if credit_score > 50:
            approval = True
        elif 30 < credit_score <= 50:
            approval = True
            corrected_interest_rate = max(loan_request['interest_rate'], 12)
        elif 10 < credit_score <= 30:
            approval = True
            corrected_interest_rate = max(loan_request['interest_rate'], 16)
        else:
            approval = False
            corrected_interest_rate = None
        
        return {
            'customer_id': customer.customer_id,
            'approval': approval,
            'interest_rate': loan_request['interest_rate'],
            'corrected_interest_rate': corrected_interest_rate,
            'tenure': loan_request['tenure'],
            'monthly_installment': calculate_monthly_installment(
                loan_request['loan_amount'], 
                corrected_interest_rate, 
                loan_request['tenure']
            ),
        }
    except Exception as e:
        return Response(
            {"error": "An error occurred while processing the request.", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
# GET /check-eligibility
class CheckEligibility(APIView):

    def get(self, request):
        try:
            data = request.data
            customer_id = data.get("customer_id")
            loan_amount = data.get("loan_amount")
            interest_rate = data.get("interest_rate")
            tenure = data.get("tenure")

            if not all([customer_id,loan_amount,interest_rate,tenure]):
                return Response(
                    {"error": "customer_id, loan_amount, interest_rate and tenure fields are required."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            loan_request = {
                    'loan_amount': loan_amount,
                    'interest_rate': interest_rate,
                    'tenure': tenure
                }
            
            customer = Customer.objects.get(customer_id=customer_id)
            eligibility = check_loan_eligibility(customer, loan_request)
            return Response(eligibility, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": "An error occurred while processing the request.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
# POST /create-loan     
class CreateLoan(APIView):
    def post(self,request):
        try:
            # Extract loan request details
            customer_id = request.data.get('customer_id')
            loan_amount = request.data.get('loan_amount')
            interest_rate = request.data.get('interest_rate')
            tenure = request.data.get('tenure')

            if not all([customer_id,loan_amount,interest_rate,tenure]):
                return Response(
                    {"error": "customer_id, loan_amount, interest_rate and tenure fields are required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Retrieve customer
            customer = Customer.objects.get(customer_id=customer_id)

            # Prepare loan request
            loan_request = {
                'loan_amount': loan_amount,
                'interest_rate': interest_rate,
                'tenure': tenure
            }

            # Check loan eligibility
            eligibility = check_loan_eligibility(customer, loan_request)

            # If loan is not approved.
            if not eligibility['approval']:
                return Response({
                    'loan_id': None,
                    'customer_id': customer_id,
                    'loan_approved': False,
                    'message': 'Loan not approved based on eligibility criteria.',
                    'monthly_installment': None
                }, status=status.HTTP_200_OK)

            # Create loan if approved.
            loan = Loan.objects.create(
                customer=customer,
                loan_amount=loan_amount,
                interest_rate=eligibility['corrected_interest_rate'] or interest_rate,
                tenure=tenure,
                monthly_installment=eligibility['monthly_installment'],
                start_date=datetime.now(),
                end_date=datetime.now() + relativedelta(months=tenure),
            )

            return Response({
                'loan_id': loan.loan_id,
                'customer_id': customer_id,
                'loan_approved': True,
                'message': 'Loan successfully approved',
                'monthly_installment': loan.monthly_installment
            }, status=status.HTTP_201_CREATED)

        except Customer.DoesNotExist:
            return Response({
                'loan_id': None,
                'customer_id': customer_id,
                'loan_approved': False,
                'message': 'Customer not found',
                'monthly_installment': None
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                'loan_id': None,
                'customer_id': customer_id,
                'loan_approved': False,
                'message': str(e),
                'monthly_installment': None
            }, status=status.HTTP_400_BAD_REQUEST)

# GET /view-loan/<loan_id>
class ViewLoanByLoanId(APIView):
    def get(self, request,loan_id):
        try:
            # Extract loan request details
            loan = Loan.objects.get(loan_id=loan_id)

            loan_data_serializer = LoanByLoanIdSerializer(loan)
            customer = loan.customer
            return Response( 
                        {**loan_data_serializer.data,
                         'customer':{
                            'customer_id':customer.customer_id,
                            'first_name' : customer.first_name,
                            'last_name': customer.last_name,
                            'first_name':customer.first_name,
                            'age':customer.age
                        }})
        except Exception as e:
            return Response(
                {"error": "An error occurred while processing the request.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# GET /view-loans/<customer_id>
class ViewLoansByCustomerId(APIView):
    def get(self, request,customer_id):
        try:
            # Extract loan request details
            loans = Loan.objects.filter(customer_id=customer_id)

            loan_serializer = LoanByCustomerIdSerializer(loans, many=True)
            return Response(loan_serializer.data)
        except Exception as e:
            return Response(
                {"error": "An error occurred while processing the request.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        