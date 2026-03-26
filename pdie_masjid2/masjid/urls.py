from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),  # homepage view
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('admin_home/', views.admin_home, name='admin_home'),
    path('treasurer_home/', views.treasurer_home, name='treasurer_home'),
    path('mainpage/', views.mainpage, name='mainpage'),  # Committee dashboard
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('submit-budget/', views.submit_budget_request, name='submit_budget_request'),
    path('request-status/', views.view_request_status, name='view_request_status'),
    path('financial-records/', views.view_financial_records, name='view_financial_records'),

    path('view_financial_records1/', views.view_financial_records1, name='view_financial_records1'),

    path('create_event/', views.create_event, name='create_event'),
    path('admin/approve_budget/', views.approve_budget_page, name='approve_budget_page'),
    path('admin/approve-budget/<int:requestid>/<str:action>/', views.process_budget_approval, name='process_budget_approval'),
    path('admin/generate-report/', views.generate_report, name='generate_report'),
    path('admin/manage-committee/', views.manage_committee, name='manage_committee'),
    path('admin/delete-committee/<int:id>/', views.delete_committee, name='delete_committee'),
    path('treasurer/manage_income/', views.manage_income, name='manage_income'),
    path('manage_expenses', views.manage_expenses, name='manage_expenses'),
    #path('expenses/edit/<int:expenseid>/', views.edit_expense, name='edit_expense'),
    #path('expenses/delete/<int:expenseid>/', views.delete_expense, name='delete_expense'),
    path('treasurer/manage-financial-record/', views.manage_financial_record, name='manage_financial_record'),
    path('income/delete/<int:incomeid>/', views.delete_income, name='delete_income'),
    path('admin/financial-records/', views.view_financial_records2, name='view_financial_records2'),








]
