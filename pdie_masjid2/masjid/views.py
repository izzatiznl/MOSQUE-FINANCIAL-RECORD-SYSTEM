from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from .models import Admin, Committee,Event,BudgetRequest,IncomeRecord,ExpenseRecord,FinancialReport
from django.db.models import Sum


# ---------------- SIGNUP (Committee Only) ----------------
def signup(request):
    if request.method == 'POST':
        committeeic = request.POST['committeeic']
        fullname = request.POST['fullname']
        username = request.POST['username']
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        gender = request.POST['gender']
        password = request.POST['password']

        if Committee.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')
        if Committee.objects.filter(committeeic=committeeic).exists():
            messages.error(request, "IC Number already registered.")
            return redirect('signup')
        if Committee.objects.filter(email=email).exists():
            messages.error(request, "Email already in use.")
            return redirect('signup')

        Committee.objects.create(
            committeeic=committeeic,
            fullname=fullname,
            username=username,
            email=email,
            phone_number=phone_number,
            gender=gender,
            password=password
        )
        messages.success(request, "Signup successful! Please login.")
        return redirect('login')

    return render(request, 'signup.html')


# ---------------- LOGIN (Committee, Admin, Treasurer) ----------------
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST['role']

        if role == 'Committee':
            try:
                user = Committee.objects.get(username=username, password=password)
                request.session['user_id'] = user.id
                request.session['user_name'] = user.fullname
                request.session['role'] = 'Committee'
                messages.success(request, f"Welcome, {user.fullname}! You have successfully logged in as Committee.")
                return redirect('mainpage')
            except Committee.DoesNotExist:
                messages.error(request, "Invalid Committee credentials.")
                return redirect('login')

        elif role in ['Administrator', 'Treasurer']:
            try:
                admin = Admin.objects.get(adminid=username, password=password, position=role)
                request.session['user_id'] = admin.adminid
                request.session['user_name'] = admin.adminid
                request.session['role'] = role

                messages.success(request, f"Welcome, {admin.adminid}! You have successfully logged in as {role}.")

                if role == 'Treasurer':
                    return redirect('treasurer_home')
                elif role == 'Administrator':
                    return redirect('admin_home')
            except Admin.DoesNotExist:
                messages.error(request, f"Invalid {role} credentials.")
                return redirect('login')

        else:
            messages.error(request, "Invalid role selected.")
            return redirect('login')

    return render(request, 'login.html')




# ---------------- LOGOUT ----------------
def logout(request):
    # Kosongkan message supaya tak terbawa ke login
    list(messages.get_messages(request))  # clear existing messages
    request.session.flush()  # remove all session data
    messages.success(request, "You have been logged out.")  # fresh message
    return redirect('login')


# ---------------- DASHBOARD PAGES ----------------
def mainpage(request):
    return render(request, 'mainpage.html')

def admin_home(request):
    return render(request, 'admin_home.html')

def treasurer_home(request):
    return render(request, 'treasurer_home.html')
def homepage(request):
    return render(request, 'home.html')



#--------------------------------mainpage----------------------------------#
def edit_profile(request):
    if 'user_id' not in request.session or request.session.get('role') != 'Committee':
        messages.error(request, "Unauthorized access.")
        return redirect('login')

    user_id = request.session.get('user_id')
    committee = Committee.objects.get(id=user_id)

    if request.method == 'POST':
        committee.committeeic = request.POST['committeeic']
        committee.fullname = request.POST['fullname']
        committee.phone_number = request.POST['phone_number']
        committee.email = request.POST['email']
        committee.gender = request.POST['gender']
        committee.save()

        messages.success(request, "Personal information updated successfully.")
        return redirect('edit_profile')

    return render(request, 'record_personal_info.html', {'committee': committee})

#-------------------------------------------------------------------------------------------------------------------

#NI REQUEST BUDGET HTML PUNYE + ni untuk submit budget jugak
def submit_budget_request(request):
    if request.method == 'POST':
        event_id = request.POST.get('eventid')
        amount = request.POST.get('amountrequested')
        reason = request.POST.get('reason')

        try:
            event = Event.objects.get(eventid=event_id)
        except Event.DoesNotExist:
            messages.error(request, "Selected event not found.")
            return redirect('submit_budget_request')

        try:
            committee = Committee.objects.get(id=request.session['user_id'])
        except Committee.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('submit_budget_request')

        # Simpan dalam DB
        BudgetRequest.objects.create(
            eventid=event,
            requestedby=committee,
            amountrequested=amount,
            reason=reason,
            status='pending'
        )

        messages.success(request, "Budget request submitted successfully.")
        return redirect('mainpage')  # <-- Tukar redirect ke mainpage untuk committee

    # GET request
    events = Event.objects.all()
    return render(request, 'request_budget.html', {'events': events})

#-----------------------------------------------------------------------------------------------------------------------
#CREATE EVENT COMMITTEE PUNYE
def create_event(request):
    if request.session.get('role') != 'Committee':
        return redirect('login')

    if request.method == 'POST':
        eventname = request.POST.get('eventname')
        eventdesc = request.POST.get('eventdesc')
        eventdate = request.POST.get('eventdate')

        committee = Committee.objects.get(id=request.session.get('user_id'))

        # Simpan event ke database
        event = Event.objects.create(
            eventname=eventname,
            eventdesc=eventdesc,
            eventdate=eventdate,
            createdby=committee
        )

        # Semak jika checkbox budget ditandakan
        if 'add_budget' in request.POST:
            amount = request.POST.get('amountrequested')
            reason = request.POST.get('reason')

            if amount and reason:
                BudgetRequest.objects.create(
                    eventid=event,
                    requestedby=committee,
                    amountrequested=amount,
                    reason=reason,
                    status='pending'
                )
                messages.success(request, "Event and budget request created successfully.")
            else:
                messages.warning(request, "Event created, but budget request was not submitted (missing amount or reason).")
        else:
            messages.success(request, "Event created successfully.")

        # Redirect ke page sendiri untuk elak resubmission
        return redirect('create_event')

    return render(request, 'create_event.html')



#----------------------------------------------------------------------------------------
def view_request_status(request):
    if 'user_id' not in request.session or request.session.get('role') != 'Committee':
        return redirect('login')

    # ASAL (SALAH: paparkan semua request)
    # requests = BudgetRequest.objects.all().order_by('-requestdate')

    # TUKAR kepada: tapis ikut siapa yang login
    committee = Committee.objects.get(id=request.session['user_id'])
    requests = BudgetRequest.objects.filter(requestedby=committee).order_by('-requestdate')

    return render(request, 'view_request_status.html', {'requests': requests})
#------------------------------------------------------------------------------------------
#ni view financial records
#committtee
def view_financial_records(request):
    income_records = IncomeRecord.objects.all().order_by('-date')
    expense_records = ExpenseRecord.objects.all().order_by('-date')

    total_income = income_records.aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = expense_records.aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expense

    return render(request, 'view_financial_records.html', {
        'income_records': income_records,
        'expense_records': expense_records,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
    })

#treasurer
def view_financial_records1(request):
    income_records = IncomeRecord.objects.all().order_by('-date')
    expense_records = ExpenseRecord.objects.all().order_by('-date')

    total_income = income_records.aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = expense_records.aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expense

    return render(request, 'view_financial_records1.html', {
        'income_records': income_records,
        'expense_records': expense_records,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance
    })


#admin
def view_financial_records2(request):
    if request.session.get('role') != 'Administrator':
        return redirect('login')

    income_records = IncomeRecord.objects.all().order_by('-date')
    expense_records = ExpenseRecord.objects.all().order_by('-date')

    total_income = income_records.aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = expense_records.aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expense

    return render(request, 'view_financial_records2.html', {
        'income_records': income_records,
        'expense_records': expense_records,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance
    })


#----------------------------------------------------------------------------------------------

#ni admin approve budget 
def approve_budget_page(request):
    if request.session.get('role') != 'Administrator':
        return redirect('login')
    
    # Preload both eventid and requestedby (committee member)
    pending_requests = BudgetRequest.objects.filter(status='pending').select_related('eventid', 'requestedby')
    
    return render(request, 'admin_approve_budget.html', {
        'pending_requests': pending_requests
    })

#-------------------------------------------------------------------------------------------------------------------
def process_budget_approval(request, requestid, action):
    if request.session.get('role') != 'Administrator':
        return redirect('login')
    
    try:
        req = BudgetRequest.objects.get(requestid=requestid)
        if action == 'approve':
            req.status = 'approved'
        elif action == 'reject':
            req.status = 'rejected'
        req.save()
        messages.success(request, f"Request #{req.requestid} successfully {req.status}.")
    except BudgetRequest.DoesNotExist:
        messages.error(request, "Request not found.")
    
    return redirect('approve_budget_page')
#-------------------------------------------------------------------------------------------
#NI GENERATE REPORT PUNYE

from django.utils import timezone  # Dah import ke belum? Kalau belum, tambah atas sekali

def generate_report(request):
    if request.session.get('role') != 'Administrator':
        return redirect('login')

    report_data = None

    if request.method == 'POST':
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']

        income_records = IncomeRecord.objects.filter(date__range=[start_date, end_date])
        expense_records = ExpenseRecord.objects.filter(date__range=[start_date, end_date])

        total_income = income_records.aggregate(Sum('amount'))['amount__sum'] or 0
        total_expense = expense_records.aggregate(Sum('amount'))['amount__sum'] or 0
        balance = total_income - total_expense

        admin = Admin.objects.get(adminid=request.session['user_id'])

        # Simpan ke database
        FinancialReport.objects.create(
            generatedby=admin,
            start_date=start_date,
            end_date=end_date,
            total_income=total_income,
            total_expense=total_expense,
            balance=balance
        )

        report_data = {
            'income_records': income_records,
            'expense_records': expense_records,
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': balance,
            'start_date': start_date,
            'end_date': end_date,
        }

        messages.success(request, "Report generated and saved to database.")

    return render(request, 'generate_report.html', {'report_data': report_data})


#------------------------------------------------------------------------------------------------------------
#manage committee
def manage_committee(request):
    if request.session.get('role') != 'Administrator':
        return redirect('login')

    committees = Committee.objects.all()
    selected = None

    if request.method == 'POST':
        id = request.POST.get('committee_id')
        if id:
            # Editing existing member
            committee = get_object_or_404(Committee, id=id)
            selected = committee
        else:
            # Adding new member
            custom_id = request.POST.get('custom_committee_id')

            # ✅ Validation: Check if ID is numeric only
            if not custom_id or not custom_id.isdigit():
                messages.error(request, "Committee ID must be numeric only (e.g. 1, 2, 100).")
                return redirect('manage_committee')

            if Committee.objects.filter(id=custom_id).exists():
                messages.error(request, "This Committee ID is already taken.")
                return redirect('manage_committee')

            committee = Committee(id=custom_id)

        # Common form fields
        committee.committeeic = request.POST['committeeic']
        committee.fullname = request.POST['fullname']
        committee.username = request.POST['username']
        committee.email = request.POST['email']
        committee.phone_number = request.POST['phone_number']
        committee.gender = request.POST['gender']
        committee.password = request.POST['password']
        committee.save()

        messages.success(request, "Committee member saved successfully.")
        return redirect('manage_committee')

    elif 'edit' in request.GET:
        selected = get_object_or_404(Committee, id=request.GET.get('edit'))

    return render(request, 'manage_committee.html', {
        'committees': committees,
        'selected': selected
    })





# ------------------------ Delete Committee Member ------------------------
def delete_committee(request, id):
    if request.session.get('role') != 'Administrator':
        messages.error(request, "Unauthorized access.")
        return redirect('login')

    committee = get_object_or_404(Committee, id=id)
    committee.delete()
    messages.success(request, "Committee member deleted.")
    return redirect('manage_committee')

#---------------------------------------------------------------------------------------------------------
#manage income
def manage_income(request):
    if request.session.get('role') != 'Treasurer':
        return redirect('login')

    income_records = IncomeRecord.objects.all().order_by('date')
    income_to_edit = None

    if request.method == 'POST':
        incomeid = request.POST['incomeid'].strip()

        # ✅ VALIDATE: incomeid must be numeric
        if not incomeid.isdigit():
            messages.error(request, "Income ID must contain digits only.")
            return redirect('manage_income')

        amount = request.POST['amount']
        source = request.POST['source']
        date = request.POST['date']

        # Edit mode
        if IncomeRecord.objects.filter(incomeid=incomeid).exists():
            income = IncomeRecord.objects.get(incomeid=incomeid)
        else:
            income = IncomeRecord(incomeid=incomeid)

        income.amount = amount
        income.source = source
        income.date = date
        income.save()

        messages.success(request, "Income record saved successfully.")
        return redirect('manage_income')

    # Edit request
    if 'edit' in request.GET:
        incomeid = request.GET.get('edit')
        income_to_edit = get_object_or_404(IncomeRecord, incomeid=incomeid)

    return render(request, 'manage_income.html', {
        'income_records': income_records,
        'income_to_edit': income_to_edit,
    })


def delete_income(request, incomeid):
    if request.session.get('role') != 'Treasurer':
        return redirect('login')
    record = get_object_or_404(IncomeRecord, incomeid=incomeid)
    record.delete()
    messages.success(request, "Income record deleted.")
    return redirect('manage_income')



#------------------------------------------------------------------------------------------------------------------
#manage expenses


def manage_expenses(request):
    if request.session.get('role') != 'Treasurer':
        return redirect('login')

    expense_to_edit = None

    if request.method == 'POST':
        expenseid = request.POST['expenseid']
        amount = request.POST['amount']
        purpose = request.POST['purpose']
        date = request.POST['date']

        # ✅ Validate expenseid is numeric only
        if not expenseid.isdigit():
            messages.error(request, "Expense ID must contain digits only.")
            return redirect('manage_expenses')

        admin = Admin.objects.get(adminid=request.session.get('user_id'))

        ExpenseRecord.objects.update_or_create(
            expenseid=expenseid,
            defaults={
                'amount': amount,
                'purpose': purpose,
                'date': date,
                'recordedby': admin
            }
        )
        messages.success(request, "Expense saved/updated successfully.")
        return redirect('manage_expenses')

    elif 'edit' in request.GET:
        expenseid = request.GET.get('edit')
        expense_to_edit = get_object_or_404(ExpenseRecord, expenseid=expenseid)

    elif 'delete' in request.GET:
        expenseid = request.GET.get('delete')
        expense = get_object_or_404(ExpenseRecord, expenseid=expenseid)
        expense.delete()
        messages.success(request, "Expense deleted.")
        return redirect('manage_expenses')

    expenses = ExpenseRecord.objects.all().order_by('-date')
    return render(request, 'manage_expenses.html', {
        'expenses': expenses,
        'expense_to_edit': expense_to_edit
    })

#-------------------------------------------------------------------------------------------------------------------
#manage financial record
def manage_financial_record(request):
    if request.session.get('role') != 'Treasurer':
        return redirect('login')

    # Kira jumlah income & expenses
    total_income = IncomeRecord.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = ExpenseRecord.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expense

    return render(request, 'manage_financial_record.html', {
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance
    })

