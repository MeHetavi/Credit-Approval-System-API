from typing import Any
from django.db import models
import uuid
# Create your models here.

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True, editable=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.IntegerField()
    phone_number = models.CharField(max_length=15, unique=True)
    monthly_salary = models.FloatField()
    approved_limit = models.FloatField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"