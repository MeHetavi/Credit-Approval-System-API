FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /api

COPY requirements.txt /api/
RUN pip install -r requirements.txt
COPY . /api/

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
