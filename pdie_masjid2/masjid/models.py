# Create your models here.
from django.db import models

class Admin(models.Model):
    adminid = models.CharField(max_length=100, primary_key=True)
    position = models.CharField(max_length=100, choices=[('Treasurer','Treasurer'),
                                                         ('Administrator','Administrator')]) 
    password = models.CharField(max_length=100)

class Committee(models.Model):
    committeeic = models.CharField(max_length=100, unique=True)
    fullname = models.CharField(max_length=200)
    username = models.CharField(max_length=200, unique=True)
    phone_number = models.CharField(max_length=15,null=True,blank=True)
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    password = models.CharField(max_length=100)


class Event(models.Model):
    eventid = models.AutoField(primary_key=True)
    eventname = models.CharField(max_length=200)
    eventdesc = models.TextField()
    eventdate = models.DateField()
    createdby = models.ForeignKey(Committee, on_delete=models.CASCADE)

class BudgetRequest(models.Model):
    requestid = models.AutoField(primary_key=True)
    eventid = models.ForeignKey(Event, on_delete=models.CASCADE)
    requestedby = models.ForeignKey(Committee, on_delete=models.CASCADE)
    amountrequested = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    requestdate = models.DateTimeField(auto_now_add=True)

class IncomeRecord(models.Model):
    incomeid = models.AutoField(primary_key=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    source = models.CharField(max_length=100)
    date = models.DateField()
    recordedby = models.ForeignKey(Admin, on_delete=models.SET_NULL, null=True)

class ExpenseRecord(models.Model):
    expenseid = models.AutoField(primary_key=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    purpose = models.CharField(max_length=100)
    date = models.DateField()
    recordedby = models.ForeignKey(Admin, on_delete=models.SET_NULL, null=True)

class FinancialReport(models.Model):
    reportid = models.AutoField(primary_key=True)
    generatedby = models.ForeignKey(Admin, on_delete=models.SET_NULL, null=True)
    generateddate = models.DateTimeField(auto_now_add=True)
    reportfile = models.FileField(upload_to='reports/', blank=True, null=True)

    # NEW FIELDS
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    total_income = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_expense = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
