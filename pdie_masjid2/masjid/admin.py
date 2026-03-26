from django.contrib import admin
from .models import Admin, Committee, Event, BudgetRequest, IncomeRecord, ExpenseRecord, FinancialReport

# Register all models to make them manageable via Django Admin
admin.site.register(Admin)
admin.site.register(Committee)
admin.site.register(Event)
admin.site.register(BudgetRequest)
admin.site.register(IncomeRecord)
admin.site.register(ExpenseRecord)
admin.site.register(FinancialReport)
