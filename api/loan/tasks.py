from celery import shared_task
import pandas as pd
from .models import Loan
from datetime import datetime
from customer.models import Customer
import os
from django.conf import settings

@shared_task
def ingest_loan_data(file_path):
    try:
        file_path = os.path.join(settings.BASE_DIR, 'loan/loan_data.xlsx')
        loan_data = pd.read_excel(file_path)
    except Exception as e:
        return f"Error reading file: {str(e)}"
    
    if not Loan.objects.all():
        for index, row in loan_data.iterrows():
            try:
                customer = Customer.objects.get(customer_id=row['Customer Id'])
                loan = Loan(
                    customer=customer,
                    loan_amount=row['Loan Amount'],
                    tenure=row['Tenure'],
                    interest_rate=row['Interest Rate'],
                    monthly_installment=row['Monthly payment'],
                    emi_paid_on_time=row['EMIs paid on Time'],
                    start_date=datetime.strptime(str(row['Date of Approval']), "%Y-%m-%d %H:%M:%S"),
                    end_date=datetime.strptime(str(row['End Date']), "%Y-%m-%d %H:%M:%S")
                )
                loan.save()

            except Customer.DoesNotExist:
                print(f"Customer with ID {row['Customer Id']} does not exist")
            except Exception as e:
                print(f"Error processing loan ID {row['Loan Id']}: {str(e)}")
    else:
        return "Loan data already ingested."
    
    return "Loan data ingestion complete."
