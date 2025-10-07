import json
from django.conf import settings
from django.shortcuts import render
from project_app.models import *
from django.contrib import messages
from django.http import HttpResponseRedirect,HttpResponse,HttpRequest,JsonResponse
from project_app.forms import *
import hashlib
from django.utils import timezone
import base64
from django.db.models import Max, F, Q
from django.shortcuts import render, get_object_or_404
from django.db import transaction
import binascii
from django.core.exceptions import ValidationError

#```````````````````````````````````````````````````*COMMON FUNCTIONS*```````````````````````````````````````````````````````````````````

def getItemNameById(tbl, cat_id):
    try:
        category = tbl.objects.get(id=cat_id).name
        return category
    except tbl.DoesNotExist:
        return 'NA'  # Default value if the record does not exist
    except Exception as e:
        return 'NA' 
    

def check_user_access(user_type, module_name, action_type):
    try:
        module = AdminModules.objects.get(name=module_name, is_active=1)
    except AdminModules.DoesNotExist:
        return False, "Module not found"

    try:
        user = AdminRoles.objects.filter(name=user_type, is_active=1).first()
        if not user:
            return False, "User not found"
        user_id = user.id
    except AdminRoles.DoesNotExist:
        return False, "User not found"

    try:
        privilege = AdminPrivilege.objects.get(
            role_id=user_id, 
            module_id=module.id,
            is_active=1,
            status=1
        )
    except AdminPrivilege.DoesNotExist:
        return False, "Access denied"

    if action_type == 'create' and not privilege.is_create:
        return False, "Access denied for create"
    
    elif action_type == 'read' and not privilege.is_read:
        return False, "Access denied for read"
    
    elif action_type == 'update' and not privilege.is_update:
        return False, "Access denied for update"
    
    elif action_type == 'delete' and not privilege.is_delete:
        return False, "Access denied for delete"

    return True, ""

#```````````````````````````````````````````````````*LOGIN DETAILS*```````````````````````````````````````````````````````````````````

def signin(request):
    return render(request,'login.html')


def admin(request):
    return render(request,'login-superadmin.html')

def login(request):
    if request.method == "POST":
        uname = request.POST.get('email')
        pwd = request.POST.get('password')
        print('uname',uname)
        print('pwd',pwd)

        hashed_pwd = hashlib.md5(pwd.encode()).hexdigest()

        if employee_table.objects.filter(email=uname, password=hashed_pwd,status=1,company_id__gte=0).exists():
            employee = employee_table.objects.get(email=uname, password=hashed_pwd)
            print('employee',employee)
            
            request.session['user_id'] = employee.id
            request.session['user_username'] = employee.username
            request.session['user_name'] = employee.name
            request.session['user_mail'] = employee.email
            request.session['company_id'] = employee.company_id
            company_name = company_table.objects.get(id=employee.company_id).name
            request.session['company_name'] = company_name

            if employee.is_admin == 1 and employee.is_superadmin == 0:
                request.session['user_type'] = 'admin'
                print(request.session['user_type'])
                return JsonResponse({"status": "success", "redirect_url": "/dashboard"})

            elif employee.is_admin == 0 and employee.is_superadmin == 0:
                request.session['user_type'] = 'staff'
                print(request.session['user_type'])
                return JsonResponse({"status": "success", "redirect_url": "/staff/dashboard"})           

        else:
            return JsonResponse({"status": "error", "message": "Email or password inorrect."})

    return JsonResponse({"status": "error", "message": "Email or password inorrect."})




def login_admin(request):
    if request.method == "POST":
        uname = request.POST.get('email')
        pwd = request.POST.get('password')
        hashed_pwd = hashlib.md5(pwd.encode()).hexdigest()

        if employee_table.objects.filter(email=uname, password=hashed_pwd, is_superadmin=1,is_admin=0,status=1,company_id=0).exists():
            employee = employee_table.objects.get(email=uname, password=hashed_pwd)
            request.session['user_id'] = employee.id
            request.session['user_username'] = employee.username
            request.session['user_name'] = employee.name
            request.session['user_mail'] = employee.email
            request.session['user_type'] = 'superadmin'
            return JsonResponse({"status": "success", "redirect_url": "/dashboard"})
        else:
            return JsonResponse({"status": "error", "message": "Email or password inorrect."})
    return JsonResponse({"status": "error", "message": "Email or password inorrect."})


def logout(request):
    if 'user_id' in request.session:
        request.session.flush() 
    return HttpResponseRedirect("/signin")


#```````````````````````````````````````````````````*DASHBOARD DETAILS*```````````````````````````````````````````````````````````````````

def dashboard(request):
    if 'user_id' in request.session:
        user_type = request.session.get('user_type')
        if user_type == 'superadmin':
            return render(request, 'superadmin/masters/dashboard.html')
        elif user_type == 'admin' :
            return render(request, 'admin/masters/dashboard.html')
        elif user_type == 'staff' :
            return render(request, 'staff/masters/dashboard.html')
        else:
            return HttpResponseRedirect("/signin")
    else:
        return HttpResponseRedirect("/signin")


#```````````````````````````````````````````````````*COMPANY DETAILS*```````````````````````````````````````````````````````````````````
def company(request):
    if 'user_id' in request.session:
        user_type = request.session.get('user_type')
        company_id = request.session.get('company_id')
        if user_type == 'admin' :
            company = company_table.objects.filter(status=1,id=company_id)            
            return render(request, 'admin/masters/company.html',{'company':company})
        elif user_type == 'superadmin' :
            company = company_table.objects.filter(status=1)
            return render(request, 'superadmin/masters/company.html',{'company':company})
        elif user_type == 'staff':
            company = company_table.objects.filter(status=1)
            return render(request, 'staff/masters/company.html', {'company':company})
        else:
            return HttpResponseRedirect("/signin")
    else:
        return HttpResponseRedirect("/signin")


def company_add(request):
    if 'user_id' in request.session:
        user_type = request.session.get('user_type')
        if user_type == 'admin':     
            company_id = request.session.get('company_id')
            employee = employee_table.objects.filter(status=1,company_id=company_id)       
            return render(request, 'admin/masters/company_add.html',{'employee':employee})
        elif user_type == 'superadmin':            
            return render(request, 'superadmin/masters/company_add.html')
        elif user_type == 'staff':            
            return render(request, 'staff/masters/company_add.html')
        else:
            return HttpResponseRedirect("/signin")
    else:
        return HttpResponseRedirect("/signin")


def fetch_technicians(request):
    vendor_id = request.GET.get('vendor_id')    
    if vendor_id:
        technicians = employee_table.objects.filter(company_id=vendor_id).values('id', 'name')
        primary_technician_id = company_table.objects.filter(id=vendor_id).values('primary_technician').first().get('primary_technician')
        return JsonResponse({
            'technicians': list(technicians),
            'primary_technician_id': primary_technician_id
        })    
    return JsonResponse({'technicians': [], 'primary_technician_id': None})

def company_report(request):
    user_type = request.session.get('user_type')
    company_id = request.session.get('company_id')
    has_access, error_message = check_user_access(user_type, "Masters/Company", "read")

    if not has_access:
        return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    company_ids = request.POST.get('company')
    query = Q(status=1) 

    if company_ids and company_ids.isdigit():
        query &= Q(id=company_ids)
    
    if user_type == 'superadmin':            
            data = list(company_table.objects.filter(query).order_by('-id').values())
    
    elif user_type == 'admin':            
            data = list(company_table.objects.filter(query,id=company_id).order_by('-id').values())

    elif user_type == 'staff':            
            data = list(company_table.objects.filter(query,id=company_id).order_by('-id').values())

    # data = list(company_table.objects.filter(query).order_by('-id').values())
    formatted = [
        {
            'id': index + 1,
            'action': '<button type="button" onclick="company_edit(\'{}\')" class="btn btn-outline-primary btn-xs"><i class="bx bxs-edit"></i></button> \
                      <button type="button" onclick="company_delete(\'{}\')" class="btn btn-outline-danger btn-xs"><i class="bx bxs-trash"></i></button>'.format(item['id'], item['id']), 
            'name': item['name'] if item['name'] else '-', 
            'logo': '<img src="/media/' + item['logo'] + '" style="width:30px; height:30px;">' if item['logo'] else '-',
            'technician': getItemNameById(employee_table, item['primary_technician']) if item['primary_technician'] else '-', 
            'prefix': item['prefix'] if item['prefix'] else '-', 
            'address': item['address_line1'] if item['address_line1'] else '-', 
            'city': item['city'] if item['city'] else '-', 
            'state': item['state'] if item['state'] else '-', 
            'phone': item['phone'] + ',' + item['mobile'] if item['phone'] else '-', 
            'email': item['email'] if item['email'] else '-', 
            'person': item['contact_person'] if item['contact_person'] else '-', 
            'cp_phone': item['cp_phone'] if item['cp_phone'] else '-', 
            'cp_mail': item['cp_email'] if item['cp_email'] else '-', 
            'report': item['report_email'] if item['report_email'] else '-', 
            'status': '<span class="badge bg-success">Active</span>' if item.get('is_active') else '<span class="badge bg-danger">Inactive</span>'
        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted})


def company_edit(request):
    if 'user_id' in request.session:
        user_id = request.session['user_id']
        user_type = request.session['user_type']
        encoded_id = request.GET.get('id', None)
        if encoded_id:
            plan_id = request.GET.get('id')
            decoded_id = base64.b64decode(encoded_id).decode('utf-8')
            company = company_table.objects.get(id=decoded_id)
            if user_type == 'superadmin':
                return render(request, 'superadmin/masters/company_edit.html', {'id': decoded_id,'company':company})
            
            elif user_type == 'staff':
                return render(request, 'staff/masters/company_edit.html', {'id': decoded_id,'company':company})
            else:
                return HttpResponseRedirect("/signin")
    else:
        return HttpResponseRedirect("/signin")
    
def company_edits(request):
    if 'user_id' in request.session:
        user_id = request.session['user_id']
        company_id = request.session['company_id']
        user_type = request.session['user_type']     
        if user_type == 'admin':
            company = company_table.objects.filter(status=1,id=company_id).first()
            return render(request, 'admin/masters/company_edit.html', {'company':company})
        
        if user_type == 'staff':
            company = company_table.objects.filter(status=1,id=company_id).first()
            return render(request, 'staff/masters/company_edit.html', {'company':company})
            
    else:
        return HttpResponseRedirect("/signin")



def update_company(request):
    if request.method == "POST":
        company_id = request.POST.get('id')
        user_id = request.session.get('user_id')
        user_type = request.session.get('user_type') 
        has_access, error_message = check_user_access(user_type, "Masters/Company", "update")

        if not has_access:
            return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})
       
        
        company_instance = company_table.objects.get(id=company_id)
        form = companyform(request.POST, request.FILES, instance=company_instance)
        
        if form.is_valid():
            primary = request.POST.get('primary_technician')

            company_instance.primary_technician = primary
            company_instance.updated_by = user_id
            company_instance.updated_on = timezone.now()
            form.save()
            return JsonResponse({'message': 'success'})
        else:
            errors = form.errors.as_json()
            return JsonResponse({'message': 'error', 'errors': errors})



from django.utils.timezone import now
from django.http import JsonResponse

def add_company_details(request):
    if request.method == "POST":
        company_id = request.POST.get('id')
        user_id = request.session.get('user_id')
        user_type = request.session.get('user_type')
        has_access, error_message = check_user_access(user_type, "Masters/Company", "create")

        if not has_access:
            return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})
        
        form = companyform(request.POST, request.FILES)

        if form.is_valid():
            # Save the company details
            company = form.save(commit=False)
            tech_name = request.POST.get('person')
            tech_phone = request.POST.get('phone')
            tech_mail = request.POST.get('mail')
            tech_pass = request.POST.get('password')

            company.updated_by = user_id
            company.created_by = user_id
            company.created_on = now()
            company.updated_on = now()
            company.save()

            company_id = company.id
            prefix = company.prefix
            employee_code = generate_employee_code(company_id,prefix)

            # Create the employee record
            hashed_password = hashlib.md5(tech_pass.encode()).hexdigest()
            employee = employee_table(
                employee_code=employee_code,
                employee_role='admin',
                user_role='',
                name=tech_name,
                username=tech_name,
                address_line1=company.address_line1,
                address_line2=company.address_line2 or '',  # Optional field
                password=hashed_password,
                city=company.city,
                country=company.country,
                postal_code=company.state,
                phone=tech_phone,
                mobile='',  # Optional field
                email=tech_mail,
                is_active=1,
                is_admin=1,
                status=1,
                created_on=now(),
                updated_on=now(),
                created_by=user_id,
                updated_by=user_id,
                company_id = company_id
            )
            employee.save()

            # Link employee to company as primary technician
            company.primary_technician = employee.id
            company.save()

            return JsonResponse({'message': 'success'})

        # Handle invalid form
        errors = {field: error.get_json_data() for field, error in form.errors.items()}
        return JsonResponse({'message': 'error', 'errors': errors})

    return JsonResponse({'message': 'Invalid request method'}, status=405)

        

def company_delete(request):
    if request.method == 'POST':
        data_id = request.POST.get('id')
        user_type = request.session.get('user_type')
        has_access, error_message = check_user_access(user_type, "Masters/Company", "delete")

        if not has_access:            
            return JsonResponse({'message': 'error', 'error_message': error_message})

        try:
            company_table.objects.filter(id=data_id).update(status=0)
            return JsonResponse({'message': 'yes'})
        except company_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})


        
#```````````````````````````````````````````````````*EMPLOYEE DETAILS*```````````````````````````````````````````````````````````````````
def employee(request):
    if 'user_id' in request.session:
        user_type = request.session.get('user_type')
        company_id = request.session.get('company_id')
        user_role = AdminRoles.objects.filter(status=1)

        if user_type == 'admin':
            employee = employee_table.objects.filter(status=1,company_id=company_id)
            company = company_table.objects.filter(status=1,id=company_id)
            supervisor = employee_table.objects.filter(status=1,company_id=company_id,is_supervisor=1)
            return render(request, 'admin/masters/employee.html', {'employee': employee,'company':company,'user_role':user_role,'supervisor':supervisor})
        elif user_type == 'superadmin':
            employee = employee_table.objects.filter(status=1)
            company = company_table.objects.filter(status=1)
            return render(request, 'superadmin/masters/employee.html', {'employee': employee,'company':company,'user_role':user_role})
        else:
            return HttpResponseRedirect("/signin")
    else:
        return HttpResponseRedirect("/signin")


def employee_view(request):
    employee_id = request.POST.get('employee')
    company_ids = request.POST.get('company')
    user_type = request.session.get('user_type')
    has_access, error_message = check_user_access(user_type, "Masters/Employee", "read")
    print('access',has_access)

    if not has_access:
        print(f"Access check failed: {error_message}")
        return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})
    
    query = Q(status=1) 

    if employee_id and employee_id.isdigit():
        query &= Q(id=employee_id)

    if company_ids and company_ids.isdigit():
        query &= Q(company_id=company_ids)  

    data = list(employee_table.objects.filter(query).order_by('-id').values())
    formatted = [
        {
            'action': '<button type="button" onclick="employee_edit(\'{}\')" class="btn btn-outline-primary btn-xs"><i class="bx bxs-edit"></i></button> \
                      <button type="button" onclick="employee_delete(\'{}\')" class="btn btn-outline-danger btn-xs"><i class="bx bxs-trash"></i></button>'.format(item['id'], item['id']), 
            'cmp': getItemNameById(company_table,  item['company_id']) if getItemNameById(company_table,  item['company_id']) else '-', 
            'name': item['name'] if item['name'] else '-', 
            'empcode': item['employee_code'] if item['employee_code'] else '-', 
            'phone': item['phone'] if item['phone'] else '-', 
            'email': item['email'] if  item['email'] else '-',              
            'status': '<span class="badge bg-success">Active</span>' if item.get('is_active') else '<span class="badge bg-danger">Inactive</span>'

        } 
        for item in data
    ]
    return JsonResponse({'data': formatted})


def employee_report(request):
    employee_id = request.POST.get('employee')
    user_type = request.session.get('user_type')
    company_id = request.session.get('company_id')
    has_access, error_message = check_user_access(user_type, "Masters/Employee", "read")
    print('access',has_access)

    if not has_access:
        print(f"Access check failed: {error_message}")
        return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})
    
    query = Q(status=1) 

    if employee_id and employee_id.isdigit():
        query &= Q(id=employee_id)  
    

    data = list(employee_table.objects.filter(query,company_id=company_id).order_by('-id').values())

    formatted = [
        {
            'action': '<button type="button" onclick="employee_edit(\'{}\')" class="btn btn-outline-primary btn-xs"><i class="bx bxs-edit"></i></button> \
                      <button type="button" onclick="employee_delete(\'{}\')" class="btn btn-outline-danger btn-xs"><i class="bx bxs-trash"></i></button>'.format(item['id'], item['id']), 
            'name': item['name'] if item['name'] else '-', 
            'empcode': item['employee_code'] if item['employee_code'] else '-', 
            'super': getItemNameById(employee_table,item['supervisor_id']) if item['supervisor_id'] else '-', 
            'phone': item['phone'] if item['phone'] else '-', 
            'email': item['email'] if  item['email'] else '-',              
            'status': '<span class="badge bg-success">Active</span>' if item.get('is_active') else '<span class="badge bg-danger">Inactive</span>'

        } 
        for item in data
    ]
    return JsonResponse({'data': formatted})



def generate_employee_code(company_id, prefix):
    if company_id != 0:
        company = company_table.objects.get(id=company_id)
        prefix = company.prefix
   
    last_employee = employee_table.objects.filter(employee_code__startswith=prefix).order_by('-id').first()
    
    if last_employee:
        last_code = last_employee.employee_code
        num_series = int(last_code.split('-')[-1]) + 1
    else:
        num_series = 1 
    employee_code = f"{prefix}-{num_series:06}"
    return employee_code

def employee_add(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        user_type = request.session.get('user_type')
        form = EmployeeForm(request.POST, request.FILES)

        has_access, error_message = check_user_access(user_type, "Masters/Employee", "create")

        if not has_access:
            return JsonResponse({'message': 'error', 'error_message': error_message})
        

        if form.is_valid():
            email = request.POST.get('email')
            category = form.save(commit=False)
            employee = request.POST.get('employee')
            name = request.POST.get('nick')
            user = request.POST.get('username')
            finger = request.POST.get('finger')
            role = request.POST.get('role')
            schd = int(request.POST.get('is_scheduler', 0))
            tech = int(request.POST.get('is_technician', 0))
            superv = int(request.POST.get('is_supervisor', 0))
            foreg = int(request.POST.get('is_foreigner', 0))
            gps = int(request.POST.get('is_gps', 0))
            pht = int(request.POST.get('is_photo', 0))
            qr = int(request.POST.get('is_qr', 0))
            signature = int(request.POST.get('is_signature', 0))
            sign = request.FILES.get('signature')
            pwd = request.POST.get('password')            
            phone = request.POST.get('phone')
            mobile = request.POST.get('mobile')
            address1 = request.POST.get('address_line1')
            address2 = request.POST.get('address_line2')
            city = request.POST.get('city')
            country = request.POST.get('country')
            postal = request.POST.get('postal')
            color = request.POST.get('color_code')  # Get color code from POST data
            vehicle = request.POST.get('vehicle')
            supervisor = request.POST.get('supervisor')
            
            company_id = request.POST.get('company')
            print('company_id',company_id)  

            if employee_table.objects.filter(email=email,company_id__gte=0).exclude(status=0).exists():
                return JsonResponse({'message': 'error', 'errors': {'email': ['This email is already in use.']}}, status=400)
            
            if company_id != 0:
                prefix = company_table.objects.get(id=company_id).prefix           
            else:
                prefix = 'CR' 
            
            # Generate employee code
            employee_code = generate_employee_code(company_id, prefix)

            category.employee_role = employee
            category.name = name
            category.supervisor_id = supervisor
            category.username = user
            category.finger_print = finger            
            category.user_role = role
            category.is_scheduler = schd
            category.is_technician = tech
            category.is_supervisor = superv
            category.is_foreigner = foreg
            category.is_gps = gps
            category.is_photo = pht
            category.is_qr = qr
            category.is_signature = signature
            category.certificate = sign  
            category.email = email
            category.password = hashlib.md5(pwd.encode()).hexdigest()
            category.phone = phone
            category.mobile = mobile 
            category.address_line1 = address1
            category.address_line2 = address2
            category.city = city
            category.country = country
            category.postal_code = postal
            category.vehicle_number = vehicle
            category.color = color  
            category.company_id = company_id  
            category.employee_code = employee_code
            category.created_by = user_id
            category.updated_by = user_id
            category.created_on = timezone.now()  
            category.updated_on = timezone.now()  
            category.save()

            return JsonResponse({'message': 'success'})
        else:
            errors = form.errors.as_json()
            return JsonResponse({'message': 'error', 'errors': errors}, status=400)

    else:
        form = EmployeeForm()
    
    return render(request, 'employee.html', {'form': form})


def employee_edit(request):
    if request.method == "POST" and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
         frm = request.POST
    data = employee_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])



def employee_update(request):
    if request.method == "POST":
        user_type = request.session.get('user_type')
        category_id = request.POST.get('id')
        category = employee_table.objects.get(id=category_id)

        has_access, error_message = check_user_access(user_type, "Masters/Employee", "update")

        if not has_access:
            return JsonResponse({'message': 'error', 'error_message': error_message})
        
        email = request.POST.get('email')

        if employee_table.objects.filter(email=email,company_id__gte=0).exclude(id=category_id).exists():
            return JsonResponse({'message': 'error', 'errors': {'email': ['This email is already in use.']}}, status=400)

        form = EmployeeForm(request.POST, request.FILES, instance=category)

        if form.is_valid():
            category = form.save(commit=False)
            
            # Extract form data
            employee = request.POST.get('employee')
            company_id = request.POST.get('company')
            name = request.POST.get('nick')
            user = request.POST.get('username')
            finger = request.POST.get('finger')
            prefix = request.POST.get('prefix')
            role = request.POST.get('role')
            schd = int(request.POST.get('is_scheduler', 0))
            tech = int(request.POST.get('is_technician', 0))
            superv = int(request.POST.get('is_supervisor', 0))
            foreg = int(request.POST.get('is_foreigner', 0))
            gps = int(request.POST.get('is_gps', 0))
            pht = int(request.POST.get('is_photo', 0))
            qr = int(request.POST.get('is_qr', 0))
            signature = int(request.POST.get('is_signature', 0))
            sign = request.FILES.get('signature')
            pwd = request.POST.get('password')            
            phone = request.POST.get('phone')
            mobile = request.POST.get('mobile')
            address1 = request.POST.get('address_line1')
            address2 = request.POST.get('address_line2')
            city = request.POST.get('city')
            country = request.POST.get('country')
            postal = request.POST.get('postal')
            color = request.POST.get('color_code')  # Get color code from POST data
            vehicle = request.POST.get('vehicle')  
            active = request.POST.get('is_active')  
            supervisor = request.POST.get('supervisor')  
            user_id = request.session.get('user_id')

            category.employee_role = employee
            category.supervisor_id = supervisor
            category.name = name
            category.username = user
            category.finger_print = finger            
            category.user_role = role
            category.is_scheduler = schd
            category.is_technician = tech
            category.is_supervisor = superv
            category.is_foreigner = foreg
            category.is_gps = gps
            category.is_photo = pht
            category.is_qr = qr
            category.is_signature = signature
            if sign:
                category.certificate = sign
            else:
                print('old')

            category.email = email
            if pwd:  
                category.password = hashlib.md5(pwd.encode()).hexdigest()
            category.phone = phone
            category.mobile = mobile 
            category.address_line1 = address1
            category.address_line2 = address2
            category.city = city
            category.country = country
            category.postal_code = postal
            category.vehicle_number = vehicle
            category.color = color  # Store the color code
            category.is_active = active
            category.company_id = company_id
            category.updated_by = user_id
            category.updated_on = timezone.now()

            # Save the category object
            category.save()            
            return JsonResponse({'message': 'success'})
        else:
            errors = form.errors.as_json()
            return JsonResponse({'message': 'error', 'errors': errors})
        

def employee_delete(request):
    if request.method == 'POST':
        data_id = request.POST.get('id')
        user_type = request.session.get('user_type')
        has_access, error_message = check_user_access(user_type, "Masters/Employee", "delete")

        if not has_access:
            print(f"Access check failed: {error_message}")
            return JsonResponse({'message': 'error', 'error_message': error_message})

        try:
            employee_table.objects.filter(id=data_id).update(status=0)
            return JsonResponse({'message': 'yes'})
        except employee_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})



#```````````````````````````````````````````````````*USER PTIVILEGE*```````````````````````````````````````````````````````````````````
def user_privilege(request):
    if 'user_id' in request.session:
        user_type = request.session.get('user_type')
        company_id = request.session.get('company_id')
        if user_type == 'superadmin':
            cmpy = company_table.objects.filter(id=1).first()
            return render(request, 'superadmin/masters/user_privilege.html', {'company': cmpy})
        if user_type == 'admin':
            cmpy = company_table.objects.filter(id=company_id).first()
            return render(request, 'admin/masters/user_privilege.html', {'company': cmpy})
        if user_type == 'staff':
            cmpy = company_table.objects.filter(id=company_id).first()
            return render(request, 'staff/masters/user_privilege.html', {'company': cmpy})
        else:
            return HttpResponseRedirect("/signin")
    else:
        return HttpResponseRedirect("/signin")
    


def get_roles(request):
    if 'user_id' in request.session:
        user_type = request.session.get('user_type')        
        print('user_type', user_type)
        
        if user_type == 'superadmin':
            roles = AdminRoles.objects.filter(status=1)
        elif user_type == 'staff':           
            # Exclude both 'admin' and 'superadmin'
            roles = AdminRoles.objects.filter(status=1).exclude(name__in=['admin', 'superadmin'])
            print('roles', roles)
        elif user_type == 'admin':           
            # Exclude only 'superadmin'
            roles = AdminRoles.objects.filter(status=1).exclude(name='superadmin')
        else:
            return JsonResponse({'error': 'Invalid user type'}, status=400)
        
        roles_data = [{'id': role.id, 'name': role.name} for role in roles]
        return JsonResponse(roles_data, safe=False)
    
    else:
        return HttpResponseRedirect("/signin")



def view_roles(request):
    role_id = request.POST.get('role_id')

    user_type = request.session.get('user_type')

    all_modules = AdminModules.objects.filter(status=1).values('id', 'name').distinct().order_by('sort_order_no')

    has_access, error_message = check_user_access(user_type, "Masters/User Privilege", "read")
    
    if not has_access:
        return JsonResponse({'data': [], 'message': 'error', 'error_message': error_message})  # Return empty list with error message

    if user_type == 'staff':
        all_modules = all_modules.filter(is_vendor=1)

    formatted = []

    if role_id:
        privileges = AdminPrivilege.objects.filter(role_id=role_id).values('module_id', 'is_create', 'is_read', 'is_update', 'is_delete')

        privilege_dict = {priv['module_id']: priv for priv in privileges}

        for item in all_modules:
            module_id = item['id']
            module_name = item['name']
            privilege_info = privilege_dict.get(module_id, None)

            if privilege_info:
                formatted.append({
                    'module_id': module_id,
                    'module': module_name,
                    'is_create': privilege_info['is_create'],
                    'is_read': privilege_info['is_read'],
                    'is_update': privilege_info['is_update'],
                    'is_delete': privilege_info['is_delete']
                })
            else:
                formatted.append({
                    'module_id': module_id,
                    'module': module_name,
                    'is_create': 0,
                    'is_read': 0,
                    'is_update': 0,
                    'is_delete': 0
                })
    else:
        formatted = [
            {
                'module_id': item['id'],
                'module': item['name'],
                'is_create': 0,
                'is_read': 0,
                'is_update': 0,
                'is_delete': 0
            }
            for item in all_modules
        ]

    return JsonResponse({'data': formatted})



# USER ROLE ADD

def add_roles(request):
    if request.method == "POST" and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        user_id = request.session['user_id']
        user_type = request.session['user_type']
        frm = request.POST
        nm = frm.get('role')
        desc = frm.get('description')
        
        has_access, error_message = check_user_access(user_type, "Masters/User Privilege", "create")

        if not has_access:
            return JsonResponse({'message': 'error', 'error_message': error_message})

        role = AdminRoles()
        role.name=nm
        role.descriptions=desc
        role.created_on=timezone.now()
        role.created_by=user_id
        role.updated_on=timezone.now()
        role.updated_by=user_id
        role.save()
        res = "Success"
        return JsonResponse({"data": res})


# USER PRIVILEGE UPDATE
def privileges_update(request):
    if request.method == 'POST':
        user_type = request.session.get('user_type')
        role_id = request.POST.get('role_id')
        privileges_json = request.POST.get('privileges')
        user_id = request.session['user_id']
        employee = get_object_or_404(employee_table, id=user_id)

        privileges = json.loads(privileges_json)

        has_access, error_message = check_user_access(user_type, "Masters/User Privilege", "update")

        if not has_access:
            return JsonResponse({'message': 'error', 'error_message': error_message})

        try:
            role = AdminRoles.objects.get(id=role_id)
        except AdminRoles.DoesNotExist:
            return JsonResponse({'error': 'Role with ID {} does not exist'.format(role_id)}, status=404)

        AdminPrivilege.objects.filter(role_id=role.id).delete()

        for privilege_data in privileges:
            module_id = privilege_data.get('module_id')  
            is_create = privilege_data.get('create', 0)
            is_read = privilege_data.get('read', 0)
            is_update = privilege_data.get('update', 0)
            is_delete = privilege_data.get('delete', 0)

            privilege = AdminPrivilege.objects.create(
                role_id=role.id,
                module_id=module_id,
                is_create=is_create,
                is_read=is_read,
                is_update=is_update,
                is_delete=is_delete,
                created_on=timezone.now(),
                updated_on=timezone.now(),
                created_by=user_id,
                updated_by=user_id
            )
            privilege.save()
        response_data = {
            'message': 'Privileges updated successfully for role ID: {}'.format(role_id)
        }
        return JsonResponse(response_data)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


# EDIT ROLES
def edit_roles(request):
    if request.method == "POST" and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
         frm = request.POST
    data = AdminRoles.objects.filter(id=request.POST.get('id'))
    return JsonResponse(data.values()[0])


# UPDATE ROLES

def update_roles(request):
    if request.method == "POST" and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        user_id = request.session['user_id']
        user_type = request.session['user_type']        
        frm = request.POST
        cid = frm.get('id')
        nm = frm.get('role')
        desc = frm.get('description')
        has_access, error_message = check_user_access(user_type, "Masters/User Privilege", "update")

        if not has_access:
            return JsonResponse({'message': 'error', 'error_message': error_message})

        role = AdminRoles.objects.get(id=cid)
        role.name=nm
        role.descriptions=desc
        role.updated_on=timezone.now()
        role.updated_by=user_id
        role.save()
        res = "Success"
        return JsonResponse({"data": res})



# DUPLICATE ROLES
def duplicate_add(request):
    if request.method == "POST" and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
         frm = request.POST
    data = AdminRoles.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])


def role_duplicate(request):
    if request.method == "POST" and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        user_id = request.session.get('user_id')
        user_type = request.session.get('user_type')
        form_data = request.POST
        original_role_id = form_data.get('duplicate_id')
        new_role_name = form_data.get('role')
        new_role_desc = form_data.get('description')

        has_access, error_message = check_user_access(user_type, "Masters/User Privilege", "update")

        if not has_access:
            return JsonResponse({'message': 'error', 'error_message': error_message})
        
        try:
            with transaction.atomic():
                original_role = AdminRoles.objects.get(id=original_role_id)
                
                new_role = AdminRoles.objects.create(
                    name=new_role_name,
                    descriptions=new_role_desc,
                    created_on=original_role.created_on,
                    created_by=original_role.created_by,
                    updated_on=timezone.now(),
                    updated_by=user_id
                )
                
                original_privileges = AdminPrivilege.objects.filter(role_id=original_role.id)
                for privilege in original_privileges:
                    new_privilege = AdminPrivilege.objects.create(
                        role_id=new_role.id,  # Use new_role.id instead of new_role
                        module_id=privilege.module_id,
                        is_create=privilege.is_create,
                        is_read=privilege.is_read,
                        is_update=privilege.is_update,
                        is_delete=privilege.is_delete,
                        created_on=timezone.now(),
                        updated_on=timezone.now(),
                        created_by=user_id,
                        updated_by=user_id
                    )
                
                return JsonResponse({"data": "Success"})
        
        except Exception as e:
            return JsonResponse({"error": str(e)})
    else:
        return JsonResponse({"error": "Invalid request method or not AJAX request"})



# DELETE ROLES
def delete_roles(request):
    if request.method == 'POST':
        data_id = request.POST.get('id')
        user_type = request.session.get('user_type')
        has_access, error_message = check_user_access(user_type, "Masters/User Privilege", "delete")
        if not has_access:
            return JsonResponse({'message': 'error', 'error_message': error_message})
        try:
            AdminRoles.objects.filter(id=data_id).update(status=0)
            return JsonResponse({'message': 'yes'})
        except AdminRoles.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})


def refresh_privileges(request):
    if request.method == 'POST':
        role_id = request.POST.get('role_id')
        modules = AdminModules.objects.filter(status=1).values('id')
        existing_privileges = AdminPrivilege.objects.filter(role_id=role_id).values_list('module_id', flat=True)
        existing_privileges_set = set(existing_privileges)  
        new_privileges = []
        for module in modules:
            module_id = module['id']
            if module_id not in existing_privileges_set:
                new_privileges.append(AdminPrivilege(
                    role_id=role_id,
                    module_id=module_id,
                    is_create=0,
                    is_read=0,
                    is_update=0,
                    is_delete=0,
                    is_active=1,
                    status=1,
                    created_on=timezone.now(),
                    updated_on=timezone.now(),
                    created_by=request.session['user_id'],  
                    updated_by=request.session['user_id']
                ))
        if new_privileges:
            AdminPrivilege.objects.bulk_create(new_privileges)
        return JsonResponse({'message': 'Privileges refreshed successfully.'})
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)





#```````````````````````````````````````````````````*CATEGORY DETAILS*```````````````````````````````````````````````````````````````````
def category(request):
    if 'user_id' in request.session:
        user_type = request.session.get('user_type')
        if user_type == 'superadmin':
            return render(request, 'superadmin/masters/category.html')
        elif user_type == 'admin':
            return render(request, 'admin/masters/category.html')
        elif user_type == 'staff':
            return render(request, 'staff/masters/category.html')
        else:
            return HttpResponseRedirect("/signin")
    else:
        return HttpResponseRedirect("/signin")
    


def category_add(request):
    if request.method == 'POST':
        user_id = request.session['user_id']
        user_type = request.session['user_type']
        has_access, error_message = check_user_access(user_type, "Masters/Category", "create")

        if not has_access:
            return JsonResponse({'message': 'error', 'error_message': error_message})

        form = categoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save(commit=False)
            photo = request.FILES.get('image')
            desc = request.POST.get('description')
            category.image = photo
            category.description = desc
            category.created_by = user_id
            category.updated_by = user_id
            category.created_on = timezone.now()
            category.updated_on = timezone.now()
            category.save()
            return JsonResponse({'message': 'success'})
        else:
            errors = form.errors.as_json()
            return JsonResponse({'message': 'error', 'errors': errors}, status=400)
    else:
        form = categoryForm()
    return render(request, 'masters/category.html', {'form': form})



def category_view(request):
    user_type = request.session.get('user_type')
    has_access, error_message = check_user_access(user_type, "Masters/Category", "read")

    if not has_access:
        return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

    data = list(category_table.objects.filter(status=1).order_by('-id').values())
    formatted = [
        {
            'id': index + 1,
            'action': '<button type="button" onclick="category_edit(\'{}\')" class="btn btn-outline-primary btn-xs"><i class="bx bxs-edit"></i></button> \
                      <button type="button" onclick="category_delete(\'{}\')" class="btn btn-outline-danger btn-xs"><i class="bx bxs-trash"></i></button>'.format(item['id'], item['id']), 
            'category': item['name'] if item['name'] else '-', 
            'description': item['description'] if item['description'] else '-', 
            'status': '<span class="badge bg-success">Active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>'  # Assuming is_active is a boolean field
        } 
        for index, item in enumerate(data)
    ]
    return JsonResponse({'data': formatted})




def category_edit(request):
    if request.method == "POST" and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
         frm = request.POST
    data = category_table.objects.filter(id=request.POST.get('id'))    
    return JsonResponse(data.values()[0])



def category_update(request):
    if request.method == "POST":
        category_id = request.POST.get('id')
        category = category_table.objects.get(id=category_id)
        form = categoryForm(request.POST, request.FILES, instance=category)
        user_type = request.session.get('user_type')
        has_access, error_message = check_user_access(user_type, "Masters/Category", "update")

        if not has_access:
            return JsonResponse({'message': 'error', 'error_message': error_message})

        if form.is_valid():
            photo = request.FILES.get('image')
            desc = request.POST.get('description')
            user_id = request.session.get('user_id')
            category.description = desc
            category.image = photo
            category.updated_by = user_id
            category.updated_on = timezone.now()
            form.save()            
            return JsonResponse({'message': 'success'})
        else:
            errors = form.errors.as_json()
            return JsonResponse({'message': 'error', 'errors': errors})


def category_delete(request):
    if request.method == 'POST':
        data_id = request.POST.get('id')
        user_type = request.session.get('user_type')
        has_access, error_message = check_user_access(user_type, "Masters/Employee", "delete")

        if not has_access:
            return JsonResponse({'message': 'error', 'error_message': error_message})
        try:
            category_table.objects.filter(id=data_id).update(status=0)
            return JsonResponse({'message': 'yes'})
        except category_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})
    

#```````````````````````````````````````````````````*CUSTOMER DETAILS*```````````````````````````````````````````````````````````````````
def customer(request):
    if 'user_id' in request.session:
        company_id = request.session.get('company_id')
        user_type = request.session.get('user_type')
        if user_type == 'admin':
            return render(request, 'admin/common/customer.html',{'company_id':company_id})
        else:
            return HttpResponseRedirect("/signin")
    else:
        return HttpResponseRedirect("/signin")
    

def customer_add(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' and request.method == "POST":
        user_id = request.session['user_id']
        user_type = request.session['user_type']
        has_access, error_message = check_user_access(user_type, "Customers", "create")

        if not has_access:
            return JsonResponse({'message': 'error', 'error_message': error_message})
        frm = request.POST
        uname = frm.get('name')
        mail = frm.get('email')
        mobile = frm.get('mobile')
        state = frm.get('state')
        country = frm.get('country')
        person = frm.get('person')
        cp_email = frm.get('cp_email')
        cp_mobile = frm.get('cp_mobile')
        cp_phone = frm.get('cp_phone')
        address = frm.get('address')
        uom = customer_table()
        uom.name=uname
        uom.mobile=mobile
        uom.email = mail
        uom.state = state
        uom.country = country
        uom.contact_person = person
        uom.cp_email = cp_email
        uom.cp_mobile = cp_mobile
        uom.cp_phone = cp_phone
        uom.address = address
        uom.created_on=timezone.now()
        uom.created_by=user_id
        uom.updated_on=timezone.now()
        uom.updated_by=user_id
        uom.save()
        res = "Success"
        return JsonResponse({"data": res})



def customer_view(request):
    user_type = request.session['user_type']
    has_access, error_message = check_user_access(user_type, "Customers", "read")

    if not has_access:
        return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})
    
    
    data = list(customer_table.objects.filter(status=1).order_by('-id').values())

    formatted = [
        {
            'action': '<button type="button" onclick="customer_edit(\'{}\')" class="btn btn-outline-primary btn-xs"><i class="bx bxs-edit"></i></button>\
                       <button type="button" onclick="customer_delete(\'{}\')" class="btn btn-outline-danger btn-xs"><i class="bx bxs-trash"></i></button>'.format(item['id'], item['id']),
            'id': index + 1,
            'name': item['name'] if item['name'] else '-',
            'mail': item['email'] if item['email'] else '-',
            'mobile': item['mobile'] if item['mobile'] else '-',
            'person': item['contact_person'] if item['contact_person'] else '-',
            'cmail': item['cp_email'] if item['cp_email'] else '-',
            'address': item['address'] if item['address'] else '-',
            'status': '<span class="badge bg-success">Active</span>' if item.get('is_active') else '<span class="badge bg-danger">Inactive</span>'
        }
        for index, item in enumerate(data)
    ]

    return JsonResponse({'data': formatted})


def customer_edit(request):
    if request.method == "POST" and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
         frm = request.POST
    data = customer_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])



def customer_update(request):
    if request.method == "POST" and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        user_id = request.session.get('user_id')
        user_type = request.session['user_type']
        has_access, error_message = check_user_access(user_type, "Customers", "update")

        if not has_access:
            return JsonResponse({'message': 'error', 'error_message': error_message})
       
        frm = request.POST
        uom_id = request.POST.get('id')
        uname = frm.get('name')
        mail = frm.get('email')
        mobile = frm.get('mobile')
        state = frm.get('state')
        country = frm.get('country')
        person = frm.get('person')
        cp_email = frm.get('cp_email')
        cp_mobile = frm.get('cp_mobile')
        cp_phone = frm.get('cp_phone')
        address = frm.get('address')
        is_active = request.POST.get('is_active')
        
        try:
            uom = customer_table.objects.get(id=uom_id)
            uom.name=uname
            uom.mobile=mobile
            uom.email = mail
            uom.state = state
            uom.country = country
            uom.contact_person = person
            uom.cp_email = cp_email
            uom.cp_mobile = cp_mobile
            uom.cp_phone = cp_phone
            uom.address = address
            uom.is_active = is_active
            uom.updated_by = user_id
            uom.updated_on = timezone.now()
            uom.save()
            return JsonResponse({'message': 'success'})
        except customer_table.DoesNotExist:
            return JsonResponse({'message': 'error', 'error_message': 'UOM not found'})
    else:
        return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})


def customer_delete(request):
    if request.method == 'POST':
        data_id = request.POST.get('id')
        user_type = request.session['user_type']
        has_access, error_message = check_user_access(user_type, "Customers", "delete")

        if not has_access:
            return JsonResponse({'message': 'error', 'error_message': error_message})

        try:
            customer_table.objects.filter(id=data_id).update(status=0)
            return JsonResponse({'message': 'yes'})
        except customer_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})
    

#```````````````````````````````````````````````````*PROJECT DETAILS*```````````````````````````````````````````````````````````````````
def project(request):
    if 'user_id' in request.session:
        company_id = request.session.get('company_id')
        user_type = request.session.get('user_type')
        if user_type == 'admin':
            incharge = employee_table.objects.filter(status=1,company_id=company_id)
            category = category_table.objects.filter(status=1)
            project = project_table.objects.filter(status=1,company_id=company_id)
            return render(request, 'admin/common/project.html',{'company_id':company_id,'incharge':incharge,'category':category,'project':project})
        elif user_type == 'staff':
            incharge = employee_table.objects.filter(status=1,company_id=company_id)
            category = category_table.objects.filter(status=1)
            project = project_table.objects.filter(status=1)
            return render(request, 'staff/common/project.html',{'company_id':company_id,'incharge':incharge,'category':category,'project':project})
        else:
            return HttpResponseRedirect("/signin")
    else:
        return HttpResponseRedirect("/signin")
    

def project_num_series():
    max_num = project_table.objects.aggregate(Max('num_series'))['num_series__max']
    if max_num is None:
        new_num = 1
    else:
        new_num = max_num + 1    
    return f"{new_num:06d}", new_num  


def project_add(request):
    if request.method == "POST" and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest': 
        user_id = request.session.get('user_id')
        company_id = request.session.get('company_id')
        user_type = request.session['user_type']
        has_access, error_message = check_user_access(user_type, "Projects", "create")

        if not has_access:
            return JsonResponse({'message': 'error', 'error_message': error_message})
        
        frm = request.POST        
        prefix = frm.get('prefix')
        title = frm.get('name')
        start = frm.get('start') or None  
        end = frm.get('end') or None     
        dead = frm.get('deadline') or None  
        incharge = frm.get('incharge')   
        mail = frm.get('email')
        mobile = frm.get('mobile')
        value = frm.get('value')
        percentage = frm.get('percentage')
        description = frm.get('description')
        category = frm.get('category')
        status = frm.get('project_status')

        if project_table.objects.filter(name=title).exists():
            return JsonResponse({"status": "Failed", "message": "Project name already exists"})

      
        project_number_str, project_number_int = project_num_series()

        project_code = f"{prefix}{project_number_str}"
        project = project_table(            
            company_id=company_id,
            prefix=prefix,
            name=title,
            start_date=start,  
            category_id=category,  
            end_date=end,      
            project_value=value,
            incharge_phone=mobile,
            incharge_email=mail,
            project_incharge=incharge,
            description=description,
            project_code=project_code,  
            deadline=dead,
            percentage=percentage,
            created_on=timezone.now(),
            created_by=user_id,
            updated_on=timezone.now(),
            updated_by=user_id,
            num_series=project_number_str ,
            project_status=status
        )
        project.save()
        return JsonResponse({"data": "Success"})    
    return JsonResponse({"error": "Invalid request"}, status=400)


def project_view(request):
    if request.method == 'POST':
        company_id = request.session.get('company_id')
        user_type = request.session['user_type']

        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        project_id = request.POST.get('project')
        status = request.POST.get('status')

        has_access, error_message = check_user_access(user_type, "Projects", "read")

        if not has_access:
            return JsonResponse({'message': 'error', 'error_message': error_message})
        
        query = Q(status=1)

        if from_date and to_date:
            query &= Q(deadline__range=[from_date, to_date])

        if project_id and project_id.isdigit():
            query &= Q(id=project_id)

        if status:
            query &= Q(project_status=status)  
       
        action = project_table.objects.filter(query,company_id=company_id).order_by('-id')
        data = list(action.values())

        formatted = [
            {
                'action': '<button type="button" onclick="project_edit(\'{}\')" class="btn btn-outline-primary btn-xs"><i class="bx bxs-edit"></i></button> \
                           <button type="button" onclick="project_delete(\'{}\')" class="btn btn-outline-danger btn-xs"><i class="bx bxs-trash"></i></button>'.format(item['id'], item['id']),
                'id': index + 1,
                'title': item['name'] if item['deadline'] else '-',
                'code': item['project_code'] if item['project_code'] else '-',
                'start': item['start_date'] if item['start_date'] else '-',
                'end': item['end_date'] if item['end_date'] else '-',
                'dead': item['deadline'] if item['deadline'] else '-',
                'incharge':  getItemNameById(employee_table, item['project_incharge']) if item['project_incharge'] else '-',
                'project': get_project_status_badge(item['project_status']),
                'mail': item['incharge_email'] if item['incharge_email'] else '-',
                'mobile': item['incharge_phone'] if item['incharge_phone'] else '-',
                'status': '<span class="badge bg-success">Active</span>' if item['is_active'] else '<span class="badge text-bg-danger">Inactive</span>'
            }
            for index, item in enumerate(data)
        ]
        return JsonResponse({'data': formatted})
    


def get_project_status_badge(task_status):
    badges = {
        'discussion': '<span class="badge bg-primary" style="font-size:10pt;">Discussion</span>',
        'in_progress': '<span class="badge bg-info" style="font-size:10pt;">In Progress</span>',
        'in_testing': '<span class="badge bg-seconday" style="font-size:10pt;">In Testing</span>',
        'completed': '<span class="badge bg-success" style="font-size:10pt;">Completed</span>',
    }
   
    return badges.get(task_status, '<span class="badge bg-primary " style="font-size:10pt;">Discussion</span>')



def project_edit(request):
    if request.method == "POST" and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
         frm = request.POST
    data = project_table.objects.filter(id=request.POST.get('id'))    
    return JsonResponse(data.values()[0])

from django.utils.dateparse import parse_date
from django.utils.timezone import now

def project_update(request):
    if request.method == "POST" and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        frm = request.POST
        user_id = request.session.get('user_id')
        company_id = request.session.get('company_id')
        uom_id = frm.get('id')

        user_type = request.session['user_type']
        has_access, error_message = check_user_access(user_type, "Projects", "update")

        if not has_access:
            return JsonResponse({'message': 'error', 'error_message': error_message})

        try:
            project = project_table.objects.get(id=uom_id)

            title = frm.get('name')
            start = parse_date(frm.get('start'))  # Convert to date or None
            end = parse_date(frm.get('end'))      # Convert to date or None
            dead = parse_date(frm.get('deadline'))  # Convert to date or None
            incharge_id = frm.get('incharge', 0)
            mail = frm.get('email')
            mobile = frm.get('mobile')
            value = frm.get('value')
            percentage = frm.get('percentage')
            description = frm.get('description')
            is_active = frm.get('is_active')
            category = frm.get('category')
            status = frm.get('project_status')

            # Check for duplicate project names
            if project_table.objects.filter(name=title).exclude(id=uom_id).exists():
                return JsonResponse({"status": "Failed", "message": "Project name already exists"})

            # Update project details
            project.company_id = company_id
            project.name = title
            project.start_date = start
            project.end_date = end
            project.deadline = dead
            project.project_value = value
            project.incharge_phone = mobile
            project.incharge_email = mail
            project.description = description
            project.percentage = percentage
            project.project_incharge = incharge_id
            project.is_active = is_active
            project.updated_by = user_id
            project.updated_on = now()
            project.category_id = category
            project.project_status = status
            project.save()

            return JsonResponse({'message': 'success'})
        except project_table.DoesNotExist:
            print(f"Project with ID {uom_id} does not exist.")
            return JsonResponse({'message': 'error', 'error_message': 'Project not found'})
    else:
        return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})

    

def project_delete(request):
    if request.method == 'POST':
        data_id = request.POST.get('id')
        user_type = request.session['user_type']
        has_access, error_message = check_user_access(user_type, "Projects", "delete")

        if not has_access:
            return JsonResponse({'message': 'error', 'error_message': error_message})
        try:
            project_table.objects.filter(id=data_id).update(status=0)
            return JsonResponse({'message': 'yes'})
        except project_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})


#```````````````````````````````````````````````````*TASK DETAILS*```````````````````````````````````````````````````````````````````


def task(request):
    if 'user_id' in request.session:
        company_id = request.session.get('company_id')
        user_type = request.session.get('user_type')
        if user_type == 'admin':
            project = project_table.objects.filter(status=1,company_id=company_id)
            staff = employee_table.objects.filter(status=1,company_id=company_id)
            return render(request, 'admin/common/task.html',{'company_id':company_id,'project':project,'staff':staff})
        elif user_type == 'staff':
            project = project_table.objects.filter(status=1,company_id=company_id)
            staff = employee_table.objects.filter(status=1,company_id=company_id,is_supervisor=0)
            return render(request, 'staff/common/task.html',{'company_id':company_id,'project':project,'staff':staff})
        else:
            return HttpResponseRedirect("/signin")
    else:
        return HttpResponseRedirect("/signin")
    



                                                       

def unique_ticket_id(company_id, project_id):
    try:
        return task_table.objects.filter(status=True, project_id=project_id, company_id=company_id).latest('num_series')
    except task_table.DoesNotExist:
        return None
 
def generate_unique_ticket_code(company_id, project_id):
    unique_id = unique_ticket_id(company_id, project_id)
    if unique_id is not None:
        product_code = str(unique_id.num_series)  # Ensure product_code is a string
        number = ''.join(filter(str.isdigit, product_code))
        print('number', number)
        print('product_code', product_code)

        if '999' in product_code and len(number) == 3:
            product_code = product_code.replace('999', '1000', 1)
        elif '9999' in product_code and len(number) == 4:
            product_code = product_code.replace('9999', '10000', 1)
        elif '99999' in product_code and len(number) == 5:
            product_code = product_code.replace('99999', '100000', 1)
        elif '999999' in product_code and len(number) == 6:
            product_code = product_code.replace('999999', '1000000', 1)
        else:
            product_code = str(int(product_code) + 1).zfill(6)
    else:
        product_code = '000001'

    return product_code


def task_add(request):
    if request.method == 'POST':
        user_id = request.session['user_id']
        company_id = request.session['company_id']
        user_type = request.session['user_type']
        has_access, error_message = check_user_access(user_type, "Tasks", "create")

        if not has_access:
            return JsonResponse({'message': 'error', 'error_message': error_message})

        form = taskForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save(commit=False)
            file = request.FILES.get('file')
            project_id = request.POST.get('project')
            task = request.POST.get('name')
            staff = request.POST.getlist('staff_id')
            
            priority = request.POST.get('priority')
            status = request.POST.get('task_status')
            start = request.POST.get('start')
            end = request.POST.get('end')
            desc = request.POST.get('descriptions')
            percent = request.POST.get('percentage')

            company = get_object_or_404(company_table, id=company_id)
            project = get_object_or_404(project_table, id=project_id)
            
            customer_prefix = company.prefix.strip()  # Remove any leading/trailing spaces
            project_prefix = project.prefix.strip()  

            num_series = generate_unique_ticket_code(company_id, project_id)

            ticket_no = f"{customer_prefix}{project_prefix}{num_series}"
            print('num_series',ticket_no)

            category.file = file
            category.descriptions = desc
            category.project_id = project_id
            category.company_id = company_id
            category.name = task
            category.staff_id = ','.join(staff)          
            category.priority = priority
            category.task_status = status
            if start and end:
                try:
                    category.start_date = start if start != '0000-00-00' else None
                    category.due_date = end if end != '0000-00-00' else None
                    
                except ValidationError:
                    return JsonResponse({'message': 'error', 'errors': "Invalid date format for warranty start or end date."}, status=400)
            category.updated_by = user_id
            category.created_by = user_id
            category.created_on = timezone.now()
            category.updated_on = timezone.now()
            category.task_code=ticket_no
            category.num_series=num_series
            category.contribution=percent
            category.save()
            return JsonResponse({'message': 'success'})
        else:
            errors = form.errors.as_json()
            return JsonResponse({'message': 'error', 'errors': errors}, status=400)
    else:
        form = categoryForm()
    return render(request, 'masters/category.html', {'form': form})

from django.db.models import Q

def task_view(request):   
    if request.method == 'POST':    
        company_id = request.session.get('company_id')            
        user_id = str(request.session.get('user_id'))  # Convert to string for comparison        
        print('user_id', user_id)    
        action = task_table.objects.filter(company_id=company_id)
        user_type = request.session.get('user_type')
        has_access, error_message = check_user_access(user_type, "Tasks", "read")

        if not has_access:
            print(f"Access check failed: {error_message}")
            return JsonResponse({'data': [], 'message': 'error', 'error_message': error_message})
            
        if user_type == 'admin':
            data = list(action.filter(status=1).order_by('-id').values())
            print('data-admin', data)

        if user_type == 'staff':
            
            data = list(action.filter(status=1).filter(Q(staff_id__contains=user_id)).order_by('-id').values())
            print('data-staff', data)

        employee_id_list = []
        for item in data:
            employee_ids = [emp_id.strip() for emp_id in item['staff_id'].split(',') if emp_id.strip()]
            employee_id_list.extend(employee_ids)

        employee_id_list = list(set(map(int, employee_id_list)))

        employees = employee_table.objects.filter(id__in=employee_id_list).values('id', 'name')
        employee_dict = {employee['id']: employee['name'] for employee in employees}

        formatted = [
            {
                'action': '<button type="button" onclick="task_edit(\'{}\')" class="btn btn-outline-primary btn-xs"><i class=" bx bxs-show me-0"></i></button>  \
                          <button type="button" onclick="task_delete(\'{}\')" class="btn btn-outline-danger btn-xs"><i class="bx bxs-trash"></i></button>'.format(item['id'], item['id']), 
                'id': index + 1, 
                'no': item['task_code'] if item['task_code'] else '-',  
                'project': getItemNameById(project_table, item['project_id']) if item['task_code'] else '-',  
                'task': item['name'] if item['name'] else '-',  
                'staff': ', '.join(f'{employee_dict.get(int(emp_id), "-")}'for emp_id in item['staff_id'].split(',') if emp_id.strip()) if item['staff_id'] else '-',
                'start': item['start_date'] if item['start_date'] else '-',  
                'end': item['due_date'] if item['due_date'] else '-',  
                'priority': item['priority'] if item['priority'] else '-',  
                'contribution': item['contribution'] if item['contribution'] else '-',  
                'task_status': item['task_status'] if item['task_status'] else '-',  
                'description': item['descriptions'] if item['descriptions'] else '-',  
                'status': '<span class="badge bg-success">Active</span>' if item['is_active'] else '<span class="badge bg-danger">Inactive</span>'  # Assuming is_active is a boolean field
            } 
            for index, item in enumerate(data)
        ]
        return JsonResponse({'data': formatted})

    



def task_edit(request):
    if 'user_id' in request.session:
        user_type = request.session.get('user_type')
        user_id  = request.session.get('user_id  ')
        encoded_id = request.GET.get('id', None)
        print('encoded_id',encoded_id)
        if encoded_id:
            decoded_id = base64.b64decode(encoded_id).decode('utf-8')
            print('decoded_id',decoded_id)
            category = category_table.objects.filter(status=1)
            if user_type == 'admin':
                return render(request, 'admin/project_tab/tab.html', {'id': decoded_id, 'category': category})
            if user_type == 'staff':
                return render(request, 'staff/tab.html', {'id': decoded_id, 'category': category})
    else:
        return HttpResponseRedirect('/signin')



def task_update(request):
    if request.method == "POST":
        brand_id = request.POST.get('id')
        brand = task_table.objects.get(id=brand_id)  # Ensure 'task_table' is imported
        user_id = request.session.get('user_id')
        company_id = request.session.get('company_id')
        form = taskForm(request.POST, request.FILES, instance=brand)  # Use 'brand' here
        user_type = request.session.get('user_type')
        has_access, error_message = check_user_access(user_type, "Tasks", "update")

        if not has_access:
            print(f"Access check failed: {error_message}")
            return JsonResponse({'data': [], 'message': 'error', 'error_message': error_message})

        if form.is_valid():
            file = request.FILES.get('file')
            project_id = request.POST.get('project')
            task = request.POST.get('name')
            staff = request.POST.getlist('staff_id')
            print('staff', staff)
            priority = request.POST.get('priority')
            status = request.POST.get('task_status')
            start = request.POST.get('start')
            end = request.POST.get('end')
            desc = request.POST.get('descriptions')
            percent = request.POST.get('percentage')
            is_active = request.POST.get('is_active')
            if start and end:
                try:
                    category.start_date = start if start != '0000-00-00' else None
                    category.due_date = end if end != '0000-00-00' else None
                    
                except ValidationError:
                    return JsonResponse({'message': 'error', 'errors': "Invalid date format for warranty start or end date."}, status=400)

            brand.file = file
            brand.descriptions = desc
            brand.project_id = project_id
            brand.company_id = company_id
            brand.name = task
            brand.contribution = percent
            brand.staff_id = ','.join(staff)
            brand.priority = priority
            brand.task_status = status           
            brand.updated_by = user_id
            brand.updated_on = timezone.now()
            brand.is_active = is_active
            form.save()  # Save the form

            return JsonResponse({'message': 'success'})
        else:
            errors = form.errors.as_json()
            return JsonResponse({'message': 'error', 'errors': errors})



def task_delete(request):
    if request.method == 'POST':
        data_id = request.POST.get('id')
        user_type = request.session.get('user_type')
        has_access, error_message = check_user_access(user_type, "Tasks", "delete")

        if not has_access:
            print(f"Access check failed: {error_message}")
            return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

        try:
            task_table.objects.filter(id=data_id).update(status=0)
            return JsonResponse({'message': 'yes'})
        except task_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})
    



def load_task_tab(request):
    if request.method == 'POST':
        tab_id = request.POST.get('tab_id')  
        item_id = request.POST.get('item_id')
        company_id = request.session.get('company_id')

        projects = get_object_or_404(task_table, id=item_id) 
        project_id= projects.project_id   

        if tab_id == 'task_details':     
            project = project_table.objects.filter(status=1,company_id=company_id)
            staff = employee_table.objects.filter(status=1,company_id=company_id,is_supervisor=0)
            task = task_table.objects.filter(id=item_id,status=1).first()
            return render(request, 'admin/project_tab/task_details.html',{'item_id':item_id,'project_id':project_id,'project':project,'staff':staff,'task':task})
        
        elif tab_id == 'important_dates': 

            return render(request, 'admin/project_tab/important_dates.html',{'item_id':item_id,'project_id':project_id})
        
        elif tab_id == 'credentials':          
                  
            return render(request, 'admin/project_tab/credentials.html',{'item_id':item_id,'project_id':project_id})

        elif tab_id == 'notes':
            return render(request, 'admin/project_tab/notes.html',{'item_id':item_id,'project_id':project_id})
        
        elif tab_id == 'file_manager':
            print('entering')
            return render(request, 'admin/project_tab/file_manager.html',{'item_id':item_id,'project_id':project_id})
        

        elif tab_id == 'to_do':
            return render(request, 'admin/project_tab/to_do.html',{'item_id':item_id,'project_id':project_id})
        

        elif tab_id == 'call_log':
            return render(request, 'admin/project_tab/call_log.html',{'item_id':item_id,'project_id':project_id})

        else:
            content = "Invalid tab selected"
            return JsonResponse({'content': content})
    else:
        return HttpResponseRedirect('/task')
    

#```````````````````````````````````````````````````*IMPORTANT DATES*```````````````````````````````````````````````````````````````````


def dates_add(request):
    if request.method == "POST" and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        user_id = request.session['user_id']
        company_id = request.session['company_id']
        frm = request.POST
        name = frm.get('name')
        date = frm.get('date')
        desc = frm.get('descriptions')
        task = frm.get('task_id')
        pro = frm.get('project_id')

        user_type = request.session.get('user_type')
        has_access, error_message = check_user_access(user_type, "Tasks", "update")

        if not has_access:
            print(f"Access check failed: {error_message}")
            return JsonResponse({'data': [], 'message': 'error', 'error_message': error_message})
        

        uom = important_table()
        uom.name=name
        uom.date=date
        uom.task_id=task
        uom.project_id=pro
        uom.descriptions=desc
        uom.company_id=company_id
        uom.created_on=timezone.now()
        uom.created_by=user_id
        uom.updated_on=timezone.now()
        uom.updated_by=user_id
        uom.save()
        res = "Success"
        return JsonResponse({"data": res})



def dates_view(request):
    task_id = request.POST.get('task') 
    user_type = request.session.get('user_type')
    has_access, error_message = check_user_access(user_type, "Tasks", "update")

    if not has_access:
        print(f"Access check failed: {error_message}")
        return JsonResponse({'data': [], 'message': 'error', 'error_message': error_message})
    

    print('task_id',task_id)
    data = list(important_table.objects.filter(status=1,task_id=task_id).order_by('-id').values())
    formatted = [
        {
            'action': '<button type="button" onclick="dates_edit(\'{}\')" class="btn btn-outline-primary btn-xs"><i class="bx bxs-edit"></i></button> \
                      <button type="button" onclick="dates_delete(\'{}\')" class="btn btn-outline-danger btn-xs"><i class="bx bxs-trash"></i></button>'.format(item['id'], item['id']), 
            'id': index + 1, 
            'name': item['name'] if  item['name'] else '-', 
            'date': item['date'] if  item['date'] else '-', 
            'desc': item['descriptions'] if  item['descriptions'] else '-',  
        } 
        for index, item in enumerate(data)
    ]
    
    return JsonResponse({'data': formatted})

def dates_edit(request):
    if request.method == "POST" and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
         frm = request.POST
    data = important_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])



def date_update(request):
    if request.method == "POST" and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        frm = request.POST
        user_id = request.session.get('user_id')
        uom_id = frm.get('id')

        user_type = request.session['user_type']
        has_access, error_message = check_user_access(user_type, "Projects", "update")

        if not has_access:
            return JsonResponse({'message': 'error', 'error_message': error_message})
        try:
            uom = important_table.objects.get(id=uom_id)
                    
            name = frm.get('name')
            date = frm.get('date')
            desc = frm.get('descriptions')
            is_active = request.POST.get('is_active')    
            uom.name=name
            uom.date=date
            uom.descriptions=desc
            uom.is_active = is_active
            uom.updated_by = user_id
            uom.updated_on = timezone.now()
            uom.save()
            return JsonResponse({'message': 'success'})
        except project_table.DoesNotExist:
            print(f"Project with ID {uom_id} does not exist.")
            return JsonResponse({'message': 'error', 'error_message': 'Project not found'})
    else:
        return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})

def dates_delete(request):
    if request.method == 'POST':
        data_id = request.POST.get('id')

        user_type = request.session.get('user_type')
        has_access, error_message = check_user_access(user_type, "Tasks", "update")

        if not has_access:
            print(f"Access check failed: {error_message}")
            return JsonResponse({'data': [], 'message': 'error', 'error_message': error_message})

        try:
            # Update the status field to 0 instead of deleting
            important_table.objects.filter(id=data_id).update(status=0)
            return JsonResponse({'message': 'yes'})
        except important_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})
    

#```````````````````````````````````````````````````*FILE MANAGER DETAILS*```````````````````````````````````````````````````````````````````


def files_add(request):
    if request.method == 'POST':
        user_id = request.session['user_id']
        company_id = request.session['company_id']
        user_type = request.session['user_type']
        has_access, error_message = check_user_access(user_type, "Masters/Category", "create")

        if not has_access:
            return JsonResponse({'message': 'error', 'error_message': error_message})

        form = fileForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save(commit=False)
            photo = request.FILES.get('file')
            project = request.POST.get('project_id')
            task = request.POST.get('task_id')
            name = request.POST.get('name')

            category.file = photo
            category.name = name
            category.project_id = project
            category.task_id = task
            category.company_id =  company_id
            category.created_by = user_id
            category.updated_by = user_id
            category.created_on = timezone.now()
            category.updated_on = timezone.now()
            category.save()
            return JsonResponse({'message': 'success'})
        else:
            errors = form.errors.as_json()
            return JsonResponse({'message': 'error', 'errors': errors}, status=400)
    else:
        form = fileForm()
    return render(request, 'masters/category.html', {'form': form})



# def file_view(request):
#     user_type = request.session.get('user_type')
#     has_access, error_message = check_user_access(user_type, "Masters/Category", "read")

#     if not has_access:
#         return JsonResponse({'data': [], 'message': 'error', 'error_message': error_message})
    
#     task_id = request.POST.get('task')
    
#     data = list(file_table.objects.filter(status=1, task_id=task_id).order_by('-id').values())
#     formatted = [] 

#     for index, item in enumerate(data):
#         file_name = item['file'] if item['file'] else None
#         if file_name:
#             file_url = f"{settings.MEDIA_URL}{file_name}"
#             print('file_url:', file_url)
        
#         formatted.append({
#             'id': index + 1,
#             'action': (
#                 '<button type="button" onclick="file_edit(\'{}\')" class="btn btn-outline-primary btn-xs">'
#                 '<i class="bx bxs-edit"></i></button> '
#                 '<button type="button" onclick="file_delete(\'{}\')" class="btn btn-outline-danger btn-xs">'
#                 '<i class="bx bxs-trash"></i></button> '
#                 '<button type="button" onclick="downloadFile(\'{}\')" class="btn btn-outline-success btn-xs">'
#                 '<i class="bx bxs-download"></i></button>'
#             ).format(item['id'], item['id'], file_name or ''),
#             'name': item['name'] if item['name'] else '-',
#             'file': file_name or '-',
#         })
    
#     return JsonResponse({'data': formatted})

from django.conf import settings
from django.http import JsonResponse
import os

def file_view(request):
    user_type = request.session.get('user_type')
    has_access, error_message = check_user_access(user_type, "Masters/Category", "read")

    if not has_access:
        return JsonResponse({'data': [], 'message': 'error', 'error_message': error_message})
    
    task_id = request.POST.get('task')
    
    data = list(file_table.objects.filter(status=1, task_id=task_id).order_by('-id').values())
    formatted = [] 

    for index, item in enumerate(data):
        file_name = item['file'] if item['file'] else None
        
        # Construct file URL if file_name exists
        file_url = os.path.join(settings.MEDIA_URL, file_name).replace('\\', '/') if file_name else None
        
        formatted.append({
            'id': index + 1,
            'action': (
                '<button type="button" onclick="file_edit(\'{}\')" class="btn btn-outline-primary btn-xs">'
                '<i class="bx bxs-edit"></i></button> '
                '<button type="button" onclick="file_delete(\'{}\')" class="btn btn-outline-danger btn-xs">'
                '<i class="bx bxs-trash"></i></button> '
                '<button type="button" onclick="downloadFile(\'{}\')" class="btn btn-outline-success btn-xs">'
                '<i class="bx bxs-download"></i></button>'
            ).format(item['id'], item['id'], file_url or ''),
            'name': item['name'] if item['name'] else '-',
            'file': file_name or '-',
        })
    
    return JsonResponse({'data': formatted})


import os
def download_file(request, file_id):
    try:
        file_obj = file_table.objects.get(id=file_id, status=1)
        file_path = file_obj.file
        print('file_obj',file_obj)
        print('file_path',file_path)
        print('os path', os.path.basename(file_path))
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type="application/octet-stream")
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            return response
    except file_table.DoesNotExist:
        return JsonResponse({'message': 'File not found'}, status=404)
    except Exception as e:
        return JsonResponse({'message': 'Error occurred while downloading the file'}, status=500)


def file_edit(request):
    if request.method == "POST" and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        frm = request.POST
    data = file_table.objects.filter(id=request.POST.get('id'))    
    return JsonResponse(data.values()[0])

from django.utils import timezone
from django.http import JsonResponse

def file_update(request):
    if request.method == "POST":
        category_id = request.POST.get('id')
        category = file_table.objects.get(id=category_id)
        form = fileForm(request.POST, request.FILES, instance=category)
        user_type = request.session.get('user_type')
        has_access, error_message = check_user_access(user_type, "Masters/Category", "update")

        if not has_access:
            return JsonResponse({'message': 'error', 'error_message': error_message})

        if form.is_valid():
            photo = request.FILES.get('file')
            name = request.POST.get('name')
            is_active = request.POST.get('is_active')
            user_id = request.session.get('user_id')

            # Update only if a new file is provided
            if photo:
                category.file = photo
            
            category.name = name
            category.is_active = is_active
            category.updated_by = user_id
            category.updated_on = timezone.now()
            form.save()            
            return JsonResponse({'message': 'success'})
        else:
            errors = form.errors.as_json()
            return JsonResponse({'message': 'error', 'errors': errors})
        


def file_delete(request):
    if request.method == 'POST':
        data_id = request.POST.get('id')

        user_type = request.session.get('user_type')
        has_access, error_message = check_user_access(user_type, "Tasks", "update")

        if not has_access:
            print(f"Access check failed: {error_message}")
            return JsonResponse({'data': [], 'message': 'error', 'error_message': error_message})

        try:
            # Update the status field to 0 instead of deleting
            file_table.objects.filter(id=data_id).update(status=0)
            return JsonResponse({'message': 'yes'})
        except file_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})
    
#```````````````````````````````````````````````````*CALL LOG*```````````````````````````````````````````````````````````````````


def call_add(request):
    if request.method == "POST" and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        user_id = request.session['user_id']
        company_id = request.session['company_id']
        frm = request.POST
        date = frm.get('date')
        desc = frm.get('descriptions')
        time = frm.get('time')
        call = frm.get('call_type')
        person = frm.get('person')
        project = frm.get('project_id')
        task = frm.get('task_id')

        user_type = request.session.get('user_type')
        has_access, error_message = check_user_access(user_type, "Tasks", "update")

        if not has_access:
            print(f"Access check failed: {error_message}")
            return JsonResponse({'data': [], 'message': 'error', 'error_message': error_message})
        

        uom = call_table()
        uom.task_id=task
        uom.project_id=project
        uom.company_id=company_id
        uom.date=date
        uom.time=time
        uom.call_type=call
        uom.contact_person=person
        uom.descriptions=desc
        uom.company_id=company_id
        uom.created_on=timezone.now()
        uom.created_by=user_id
        uom.updated_on=timezone.now()
        uom.updated_by=user_id
        uom.save()
        res = "Success"
        return JsonResponse({"data": res})



def call_view(request):
    task_id = request.POST.get('task') 
    user_type = request.session.get('user_type')
    has_access, error_message = check_user_access(user_type, "Tasks", "update")

    if not has_access:
        print(f"Access check failed: {error_message}")
        return JsonResponse({'data': [], 'message': 'error', 'error_message': error_message})
    

    print('task_id',task_id)
    data = list(call_table.objects.filter(status=1,task_id=task_id).order_by('-id').values())
    formatted = [
        {
            'action': '<button type="button" onclick="call_edit(\'{}\')" class="btn btn-outline-primary btn-xs"><i class="bx bxs-edit"></i></button> \
                      <button type="button" onclick="call_delete(\'{}\')" class="btn btn-outline-danger btn-xs"><i class="bx bxs-trash"></i></button>'.format(item['id'], item['id']), 
            'id': index + 1, 
            'date': item['date'] if  item['date'] else '-', 
            'time': item['time'] if  item['time'] else '-', 
            'call': item['call_type'] if  item['call_type'] else '-', 
            'contact': item['contact_person'] if  item['contact_person'] else '-', 
            'desc': item['descriptions'] if  item['descriptions'] else '-',  
        } 
        for index, item in enumerate(data)
    ]
    
    return JsonResponse({'data': formatted})

def call_edit(request):
    if request.method == "POST" and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
         frm = request.POST
    data = call_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])



def call_update(request):
    if request.method == "POST" and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        frm = request.POST
        user_id = request.session.get('user_id')
        uom_id = frm.get('id')

        user_type = request.session['user_type']
        has_access, error_message = check_user_access(user_type, "Projects", "update")

        if not has_access:
            return JsonResponse({'message': 'error', 'error_message': error_message})
        try:
            uom = call_table.objects.get(id=uom_id)
                    
            date = frm.get('date')
            time = frm.get('time')
            call = frm.get('call_type')
            person = frm.get('person')
            desc = frm.get('descriptions')

            uom.time=time
            uom.date=date
            uom.descriptions=desc
            uom.call_type = call
            uom.contact_person = person
            uom.updated_by = user_id
            uom.updated_on = timezone.now()
            uom.save()
            return JsonResponse({'message': 'success'})
        except project_table.DoesNotExist:
            print(f"Project with ID {uom_id} does not exist.")
            return JsonResponse({'message': 'error', 'error_message': 'Project not found'})
    else:
        return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})

def call_delete(request):
    if request.method == 'POST':
        data_id = request.POST.get('id')

        user_type = request.session.get('user_type')
        has_access, error_message = check_user_access(user_type, "Tasks", "update")

        if not has_access:
            print(f"Access check failed: {error_message}")
            return JsonResponse({'data': [], 'message': 'error', 'error_message': error_message})

        try:
            # Update the status field to 0 instead of deleting
            call_table.objects.filter(id=data_id).update(status=0)
            return JsonResponse({'message': 'yes'})
        except call_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})
    


#```````````````````````````````````````````````````*NOTES DETAILS*```````````````````````````````````````````````````````````````````


def notes_add(request):
    if request.method == "POST" and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        user_id = request.session['user_id']
        company_id = request.session['company_id']
        frm = request.POST
        date = frm.get('date')
        title = frm.get('title')
        desc = frm.get('descriptions')
        short = frm.get('short_descriptions')
        project = frm.get('project_id')
        task = frm.get('task_id')

        user_type = request.session.get('user_type')
        has_access, error_message = check_user_access(user_type, "Tasks", "update")

        if not has_access:
            print(f"Access check failed: {error_message}")
            return JsonResponse({'data': [], 'message': 'error', 'error_message': error_message})
        

        uom = notes_table()
        uom.task_id=task
        uom.project_id=project
        uom.company_id=company_id
        uom.date=date
        uom.title=title
        uom.short_descriptions=short
        uom.descriptions=desc
        uom.company_id=company_id
        uom.created_on=timezone.now()
        uom.created_by=user_id
        uom.updated_on=timezone.now()
        uom.updated_by=user_id
        uom.save()
        res = "Success"
        return JsonResponse({"data": res})

        
def notes_view(request):
    task_id = request.POST.get('task') 
    user_type = request.session.get('user_type')
    has_access, error_message = check_user_access(user_type, "Tasks", "update")

    if not has_access:
        print(f"Access check failed: {error_message}")
        return JsonResponse({'data': [], 'message': 'error', 'error_message': error_message})
    

    print('task_id',task_id)
    data = list(notes_table.objects.filter(status=1,task_id=task_id).order_by('-id').values())
    formatted = [
        {
            'action': '<button type="button" onclick="notes_edit(\'{}\')" class="btn btn-outline-primary btn-xs"><i class="bx bxs-edit"></i></button> \
                      <button type="button" onclick="notes_delete(\'{}\')" class="btn btn-outline-danger btn-xs"><i class="bx bxs-trash"></i></button>'.format(item['id'], item['id']), 
            'id': index + 1, 
            'date': item['date'] if  item['date'] else '-', 
            'title': item['title'] if  item['title'] else '-', 
            'short': item['short_descriptions'] if  item['short_descriptions'] else '-',  
        } 
        for index, item in enumerate(data)
    ]
    
    return JsonResponse({'data': formatted})

def notes_edit(request):
    if request.method == "POST" and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
         frm = request.POST
    data = notes_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])


def notes_update(request):
    if request.method == "POST" and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        frm = request.POST
        user_id = request.session.get('user_id')
        uom_id = frm.get('id')

        user_type = request.session['user_type']
        has_access, error_message = check_user_access(user_type, "Projects", "update")

        if not has_access:
            return JsonResponse({'message': 'error', 'error_message': error_message})
        try:
            uom = notes_table.objects.get(id=uom_id)
                    
            date = frm.get('date')
            title = frm.get('title')
            desc = frm.get('descriptions')
            print('desc',desc)
            short = frm.get('short_descriptions')

            uom.date=date
            uom.title=title
            uom.short_descriptions=short
            uom.descriptions=desc
            uom.updated_by = user_id
            uom.updated_on = timezone.now()
            uom.save()
            return JsonResponse({'message': 'success'})
        except notes_table.DoesNotExist:
            print(f"Project with ID {uom_id} does not exist.")
            return JsonResponse({'message': 'error', 'error_message': 'Project not found'})
    else:
        return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})
    


def notes_delete(request):
    if request.method == 'POST':
        data_id = request.POST.get('id')

        user_type = request.session.get('user_type')
        has_access, error_message = check_user_access(user_type, "Tasks", "update")

        if not has_access:
            print(f"Access check failed: {error_message}")
            return JsonResponse({'data': [], 'message': 'error', 'error_message': error_message})

        try:
            # Update the status field to 0 instead of deleting
            notes_table.objects.filter(id=data_id).update(status=0)
            return JsonResponse({'message': 'yes'})
        except notes_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})



#```````````````````````````````````````````````````*CREDENTIALS  DETAILS*```````````````````````````````````````````````````````````````````

def credentials_delete(request):
    if request.method == 'POST':
        data_id = request.POST.get('id')

        user_type = request.session.get('user_type')
        has_access, error_message = check_user_access(user_type, "Tasks", "update")

        if not has_access:
            print(f"Access check failed: {error_message}")
            return JsonResponse({'data': [], 'message': 'error', 'error_message': error_message})

        try:
            # Update the status field to 0 instead of deleting
            credentials_table.objects.filter(id=data_id).update(status=0)
            return JsonResponse({'message': 'yes'})
        except credentials_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})
    


def credentials_add(request):
    if request.method == "POST" and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        user_id = request.session['user_id']
        company_id = request.session['company_id']
        frm = request.POST
        name = frm.get('name')
        user  = frm.get('username')
        mail = frm.get('email')
        pwd = frm.get('password')
        desc = frm.get('descriptions')
        project = frm.get('project_id')
        task = frm.get('task_id')

        user_type = request.session.get('user_type')
        has_access, error_message = check_user_access(user_type, "Tasks", "update")

        if not has_access:
            print(f"Access check failed: {error_message}")
            return JsonResponse({'data': [], 'message': 'error', 'error_message': error_message})
        

        uom = credentials_table()
        uom.task_id=task
        uom.project_id=project
        uom.company_id=company_id
        uom.name=name
        uom.username=user
        uom.email=mail
        uom.password=pwd
        uom.descriptions=desc
        uom.company_id=company_id
        uom.created_on=timezone.now()
        uom.created_by=user_id
        uom.updated_on=timezone.now()
        uom.updated_by=user_id
        uom.save()
        res = "Success"
        return JsonResponse({"data": res})



def credentials_view(request):
    task_id = request.POST.get('task') 
    user_type = request.session.get('user_type')
    has_access, error_message = check_user_access(user_type, "Tasks", "update")

    if not has_access:
        print(f"Access check failed: {error_message}")
        return JsonResponse({'data': [], 'message': 'error', 'error_message': error_message})
    

    print('task_id',task_id)
    data = list(credentials_table.objects.filter(status=1,task_id=task_id).order_by('-id').values())
    formatted = [
        {
            'action': '<button type="button" onclick="credentials_edit(\'{}\')" class="btn btn-outline-primary btn-xs"><i class="bx bxs-edit"></i></button> \
                      <button type="button" onclick="credentials_delete(\'{}\')" class="btn btn-outline-danger btn-xs"><i class="bx bxs-trash"></i></button>'.format(item['id'], item['id']), 
            'id': index + 1, 
            'name': item['name'] if  item['name'] else '-', 
            'username': item['username'] if  item['username'] else '-', 
            'mail': item['email'] if  item['email'] else '-',  
            'pass': item['password'] if  item['password'] else '-',  
        } 
        for index, item in enumerate(data)
    ]
    
    return JsonResponse({'data': formatted})


def credentials_edit(request):
    if request.method == "POST" and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
         frm = request.POST
    data = credentials_table.objects.filter(id=request.POST.get('id'))
    
    return JsonResponse(data.values()[0])


def credentials_update(request):
    if request.method == "POST" and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        frm = request.POST
        user_id = request.session.get('user_id')
        uom_id = frm.get('id')

        user_type = request.session['user_type']
        has_access, error_message = check_user_access(user_type, "Projects", "update")

        if not has_access:
            return JsonResponse({'message': 'error', 'error_message': error_message})
        try:
            uom = credentials_table.objects.get(id=uom_id)
            name = frm.get('name')
            user  = frm.get('username')
            mail = frm.get('email')
            pwd = frm.get('password')
            desc = frm.get('descriptions')

            uom.name=name
            uom.username=user
            uom.email=mail
            uom.password=pwd
            uom.descriptions=desc
            uom.updated_by = user_id
            uom.updated_on = timezone.now()
            uom.save()
            return JsonResponse({'message': 'success'})
        except credentials_table.DoesNotExist:
            print(f"Project with ID {uom_id} does not exist.")
            return JsonResponse({'message': 'error', 'error_message': 'Project not found'})
    else:
        return JsonResponse({'message': 'error', 'error_message': 'Invalid request'})
    

#```````````````````````````````````````````````````*TO-DO DETAILS*```````````````````````````````````````````````````````````````````


def create_todo(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        project_id = request.POST.get('project_id')
        company_id = request.session.get('company_id')
        user_id = request.session.get('user_id')
        name = request.POST.get('name')

        
        todo = todo_table.objects.create(
            task_id=task_id,
            project_id=project_id,
            company_id=company_id,
            todo_status="opened",  
            name=name,
            is_active=1,
            status=1,
            created_on=timezone.now(),
            updated_on=timezone.now(),
            created_by=user_id,
            updated_by=user_id
        )

        return JsonResponse({'message': 'success', 'todo_id': todo.id, 'name': todo.name})
    return JsonResponse({'message': 'error'})



def delete_todo(request):
    if request.method == 'POST':
        todo_id = request.POST.get('todo_id')
        try:
            todo = todo_table.objects.get(id=todo_id)
            todo.status = 0  
            todo.save()  
            return JsonResponse({'message': 'success'})
        except todo_table.DoesNotExist:
            return JsonResponse({'message': 'error'})



def get_todo_list(request):
    task_id = request.GET.get('task_id')  # Get task_id from the request

    # Fetch todos from the database, filter by task_id
    todos = todo_table.objects.filter(task_id=task_id)  # Ensure this fetches the required todos

    # Prepare the list of todos, include status
    todos_data = [{
        'todo_id': todo.id,
        'name': todo.name,
        # Map the text status to numeric value (1 for completed, 0 for opened)
        'todo_status': 'completed' if todo.todo_status == 'completed' else 'opened',
    } for todo in todos]

    print('todos_data', todos_data)
    return JsonResponse({'todos': todos_data})





def toggle_status(request):
    todo_id = request.POST.get('todo_id')
    status = request.POST.get('status')

    try:
        todo = todo_table.objects.get(id=todo_id)
        if status == 'completed':
            todo.todo_status = 'completed'
        else:
            todo.todo_status = 'opened'
        todo.save()
        return JsonResponse({'message': 'success'})
    except todo_table.DoesNotExist:
        return JsonResponse({'message': 'error'}, status=400)


#```````````````````````````````````````````````````*STAFF LOG  DETAILS*```````````````````````````````````````````````````````````````````

def staff_log(request):
    if 'user_id' in request.session:
        company_id = request.session.get('company_id')
        user_type = request.session.get('user_type')
        if user_type == 'admin':
            project = project_table.objects.filter(status=1,company_id=company_id)
            print('project',project)
            return render(request, 'admin/common/staff_log.html',{'company_id':company_id,'project':project})
        elif user_type == 'superadmin':
            project = project_table.objects.filter(status=1)
            company = company_table.objects.filter(status=1)
            staff = employee_table.objects.filter(status=1)
            return render(request, 'superadmin/masters/staff_log.html',{'company':company,'staff':staff,'project':project})  
        else:
            return HttpResponseRedirect("/signin")
    else:
        return HttpResponseRedirect("/signin")
    
    
def fetch_task(request, project_id):
    company_id = request.session.get('company_id')
    user_type = request.session.get('user_type')
    if user_type == 'admin':
        try:
            projects = task_table.objects.filter(project_id=project_id,company_id=company_id,status=1).values('id', 'name')
            return JsonResponse({'projects': list(projects)}, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    elif user_type == 'staff':       
        try:
            projects = task_table.objects.filter(project_id=project_id,company_id=company_id,status=1).values('id', 'name')
            return JsonResponse({'projects': list(projects)}, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    
def staff_log_view(request):
    user_type = request.session.get('user_type')
    user_id = request.session.get('user_id')
    company_id = request.session.get('company_id')
    has_access, error_message = check_user_access(user_type, "Staff Log", "read")



    if not has_access:
        return JsonResponse({'data': [], 'message': 'error', 'error_message': error_message})
    
    if user_type == 'superadmin':
        logs = log_table.objects.filter(status=1)

    supervisor = employee_table.objects.filter(id=user_id, is_supervisor=1).first()
    if not supervisor:
        return JsonResponse({'data': [], 'message': 'error', 'error_message': 'Supervisor not found.'})

    supervised_employees = employee_table.objects.filter(
        supervisor_id=supervisor.id, is_active=1
    ).values_list("id", flat=True)

    # Convert to string for consistent filtering
    supervised_employees_ids = [str(emp_id) for emp_id in supervised_employees]

    # Logs filtering logic
    logs = log_table.objects.filter(
        company_id=company_id,
        status=1,
    ).filter(
        # Staff ID is either supervised by the supervisor or matches the logged-in user
        Q(staff_id__in=supervised_employees_ids) | Q(staff_id=str(user_id))
    ).order_by("-id")

    print('logs', logs)

    formatted = []
    for index, log in enumerate(logs):
        # Conditions for showing "Approve" button
        is_staff_supervised = str(log.staff_id) in supervised_employees_ids
        is_logged_in_user = str(log.staff_id) == str(user_id)
        is_not_approved = log.is_approved != 1
        is_task_completed = log.task_status == 'completed'

        # Debugging conditions
        print(f"Log ID: {log.id}")
        print(f"  Is staff supervised: {is_staff_supervised}")
        print(f"  Is logged in user: {is_logged_in_user}")
        print(f"  Is not approved: {is_not_approved}")
        print(f"  Is task completed: {is_task_completed}")

        # Construct the "Approve" button based on conditions
        approve_button = ""
        if (is_staff_supervised or is_logged_in_user) and is_not_approved:
            approve_button = '<button type="button" onclick="log_approval(\'{}\')" class="btn btn-outline-success btn-xs"><i class="bx bx-check"></i>Approve</button>'.format(log.id)

        action_buttons = '<button type="button" onclick="log_delete(\'{}\')" class="btn btn-outline-danger btn-xs"><i class="bx bxs-trash"></i></button> \
                          <button type="button" onclick="log_edit(\'{}\')" class="btn btn-outline-primary btn-xs"><i class="bx bxs-edit"></i></button> {}'.format(log.id, log.id, approve_button)

        formatted.append({
            "id": index + 1,
            "action": action_buttons,
            "from": log.start_date if log.start_date else "-",
            "to": log.to_date if log.to_date else "-",
            "start": log.start_time if log.start_time else "-",
            "end": log.end_time if log.end_time else "-",
            "project": getItemNameById(project_table, log.project_id) if log.project_id else "-",
            "task": getItemNameById(task_table, log.task_id) if log.task_id else "-",
            "staff": getItemNameById(employee_table, log.staff_id) if log.staff_id else "-",
            "desc": log.task_descriptions if log.task_descriptions else "-",
            "issue": log.issue_descriptions if log.issue_descriptions else "-",
            'approve': '<span class="badge bg-success">Approved</span>' if log.is_approved else '<span class="badge bg-danger">Pending</span>',
            "status": get_task_status_badge(log.task_status),
        })

    return JsonResponse({'data': formatted})

def log_details(request):
    user_type = request.session.get('user_type')
    user_id = request.session.get('user_id')
    company_id = request.POST.get('company_id')
    project_id = request.POST.get('project')
    staff_id = request.POST.get('staff')
    
    has_access, error_message = check_user_access(user_type, "Staff Log", "read")

    if not has_access:
        return JsonResponse({'data': [], 'message': 'error', 'error_message': error_message})  

    query = Q(status=1)

    print(f"Company ID: {company_id}, Project ID: {project_id}, Staff ID: {staff_id}")  # Debug input

    if company_id and str(company_id).isdigit():
        query &= Q(company_id=company_id)

    if project_id and str(project_id).isdigit():
        query &= Q(project_id=project_id)

    if staff_id and str(staff_id).isdigit():
        query &= Q(staff_id__contains=staff_id)  # NOTE: may cause false positives

    print(f"Final Query: {query}")  # Debug query construction

    logs = log_table.objects.filter(query)

    print(f"Logs fetched: {logs.count()}")  # Debug result count

    formatted = []
    for index, log in enumerate(logs):
        action_buttons = (
            '<button type="button" onclick="log_delete(\'{}\')" class="btn btn-outline-danger btn-xs">'
            '<i class="bx bxs-trash"></i></button> '
            '<button type="button" onclick="log_edit(\'{}\')" class="btn btn-outline-primary btn-xs">'
            '<i class="bx bxs-edit"></i></button>'
        ).format(log.id, log.id)

        formatted.append({
            "id": index + 1,
            "action": action_buttons,
            "from": log.start_date if log.start_date else "-",
            "to": log.to_date if log.to_date else "-",
            "start": log.start_time if log.start_time else "-",
            "end": log.end_time if log.end_time else "-",
            "project": getItemNameById(project_table, log.project_id) if log.project_id else "-",
            "task": getItemNameById(task_table, log.task_id) if log.task_id else "-",
            "staff": getItemNameById(employee_table, log.staff_id) if log.staff_id else "-",
            "desc": log.task_descriptions if log.task_descriptions else "-",
            "issue": log.issue_descriptions if log.issue_descriptions else "-",
            "approve": '<span class="badge bg-success">Approved</span>' if log.is_approved else '<span class="badge bg-danger">Pending</span>',
            "status": get_task_status_badge(log.task_status),
        })

    return JsonResponse({'data': formatted})


def get_task_status_badge(task_status):
    badges = {
        'pending': '<span class="badge bg-warning text-dark">Pending</span>',
        'in_progress': '<span class="badge bg-info text-dark">In Progress</span>',
        'completed': '<span class="badge bg-success">Completed</span>',
        'on_hold': '<span class="badge bg-secondary">On Hold</span>',
        'failed': '<span class="badge bg-danger">Failed</span>',
    }
    # Default to 'Pending' if the status is unknown
    return badges.get(task_status, '<span class="badge bg-warning text-dark">Pending</span>')


def log_delete(request):
    if request.method == 'POST':
        data_id = request.POST.get('id')
        user_type = request.session.get('user_type')
        has_access, error_message = check_user_access(user_type, "Tasks", "delete")

        if not has_access:
            print(f"Access check failed: {error_message}")
            return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

        try:
            log_table.objects.filter(id=data_id).update(status=0)
            return JsonResponse({'message': 'yes'})
        except log_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})
    


def log_approval(request):
    if request.method == 'POST':
        data_id = request.POST.get('id')
        user_type = request.session.get('user_type')
        user_id = request.session.get('user_id')
        has_access, error_message = check_user_access(user_type, "Tasks", "delete")

        if not has_access:
            print(f"Access check failed: {error_message}")
            return JsonResponse({'data':[],'message': 'error', 'error_message': error_message})

        try:
            log_table.objects.filter(id=data_id).update(is_approved=1,approved_by=user_id)
            return JsonResponse({'message': 'yes'})
        except log_table.DoesNotExist:
            return JsonResponse({'message': 'no such data'})
    else:
        return JsonResponse({'message': 'Invalid request method'})
    


