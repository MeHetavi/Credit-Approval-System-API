# Generated by Django 5.1.3 on 2024-12-04 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('customer_id', models.AutoField(editable=False, primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('age', models.IntegerField()),
                ('phone_number', models.CharField(max_length=15, unique=True)),
                ('monthly_salary', models.FloatField()),
                ('approved_limit', models.FloatField()),
                ('current_debt', models.FloatField(default=0.0)),
            ],
        ),
    ]
