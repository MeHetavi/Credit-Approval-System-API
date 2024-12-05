from celery import shared_task
import pandas as pd
from datetime import datetime
from .models import Customer
import os
from django.conf import settings
@shared_task
def ingest_customer_data(file_path='customer_data.xlsx'):
    
    try:
        file_path = os.path.join(settings.BASE_DIR, f'customer/{file_path}')
        customer_data = pd.read_excel(file_path)
    except Exception as e:
        return f"Error reading file: {str(e)}"
    
    for index, row in customer_data.iterrows():
        try:
            if not Customer.objects.all():
                customer = Customer(
                    first_name=row['First Name'],
                    last_name=row['Last Name'],
                    age=row['Age'],
                    phone_number=row['Phone Number'],
                    monthly_salary=row['Monthly Salary'],
                    approved_limit=row['Approved Limit'],
                    )
                customer.save()
            else:
                return "Customer data already ingested."

        except Exception as e:
            break
    
    return "Customer data ingestion complete."
