from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Customer
from .serializers import CustomerSerializer

# POST /register
class RegisterCustomer(APIView):
    def post(self, request):
        try:
            # Retrieve customer data.
            data = request.data
            first_name = data.get("first_name")
            last_name = data.get("last_name")
            age = data.get("age")
            monthly_salary = data.get("monthly_income")
            phone_number = data.get("phone_number")

            if not all([first_name, last_name, age, monthly_salary, phone_number]):
                return Response(
                    {"error": "All fields are required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            approved_limit = round((36 * monthly_salary) / 100000) * 100000  # Nearest lakh

            customer = Customer.objects.create(
                first_name=first_name,
                last_name=last_name,
                age=age,
                monthly_salary=monthly_salary,
                phone_number=phone_number,
                approved_limit=approved_limit
            )

            response_data = CustomerSerializer(customer).data
            return Response({
                                'data':response_data,
                                'message':"Customer created successfully."
                             }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": "An error occurred while processing the request.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )