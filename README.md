# Credit-Approval-System-API

1. Clone the repo.

2. Create a .env file in the api folder, where DockerFile is present.

3. Set the .env variables.
    - POSTGRES_USER
    - POSTGRES_PASSWORD
    - POSTGRES_DB=credit_db
    - POSTGRES_HOST=db
    - POSTGRES_PORT=5432

4. docker-compose up --build
    - The data will not be injested as the migrations are yet to be made.

5. Open the docker shell and make migrations.
    - docker exec -it api-django-1  /bin/bash
    - python manage.py makemigrations
    - python manage.py migrate

6. Rerun the docker file to injest all data to db.

7. Open postman and check following endpoints:
    - POST /register
        - {
            "first_name" : "Hetavi",
            "last_name" : "Shah",
            "age" : 19,
            "monthly_income" : 1000,
            "phone_number" : 9876543210
        }
    - GET /check-eligibility
        - {
            "customer_id": 14/40/114,
            "loan_amount":100000,
            "interest_rate": 10,
            "tenure": 20
        }
    - POST /create-loan
        - {
            "customer_id": 14/40/114,
            "loan_amount":100000,
            "interest_rate": 10,
            "tenure": 20
        }
    - GET /view-loan/<loan_id>
    - GET /view-loans/<customer_id>