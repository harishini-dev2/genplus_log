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

#```````````````````````````````````````````````````*DASHBOARD DETAILS*```````````````````````````````````````````````````````````````````

def staff_dashboard(request):
    if 'user_id' in request.session:
        user_type = request.session.get('user_type')
        if user_type == 'staff':
            return render(request, 'staff/masters/dashboard.html')        
        else:
            return HttpResponseRedirect("/signin")
    else:
        return HttpResponseRedirect("/signin")


#```````````````````````````````````````````````````*DASHBOARD DETAILS*```````````````````````````````````````````````````````````````````

def log_entry(request):
    if 'user_id' in request.session:
        user_type = request.session.get('user_type')
        if user_type == 'staff':
            return render(request, 'staff/common/staff_log.html')               
        else:
            return HttpResponseRedirect("/signin")
    else:
        return HttpResponseRedirect("/signin")
    

def fetch_projects(request):
    if request.method == "GET":
        company_id = request.session.get('company_id')
        staff_id = request.session.get('user_id')

        try:
          
            project_ids = task_table.objects.filter(
                company_id=company_id,
                status=1,
                staff_id__icontains=staff_id
            ).values_list('project_id', flat=True).distinct()
            print('project_ids',project_ids)

            
            projects = project_table.objects.filter(
                id__in=project_ids,
                company_id=company_id,
                status=1
            ).values('id', 'name')

            return JsonResponse({'projects': list(projects)}, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


def fetch_tasks(request, project_id):
    if request.method == "GET":
        company_id = request.session.get('company_id')
        staff_id = request.session.get('user_id')

        try:
           
            tasks = task_table.objects.filter(
                project_id=project_id,
                company_id=company_id,
                status=1,
                staff_id__icontains=staff_id
            ).values('id', 'task_code', 'project_id','name')

           
            # Add project task names to each task
            tasks_with_names = [
                {
                    'id': task['id'],
                    'task_code': task['task_code'],
                    'task_name': task['name']
                }
                for task in tasks
            ]

            return JsonResponse({'tasks': tasks_with_names}, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        

def log_add(request):
    if request.method == 'POST':
        user_id = request.session['user_id']
        print('user_id',user_id)
        employee = employee_table.objects.filter(status=1,id=user_id).first()
        print('employee',employee)
        company_id = request.session['company_id']
        user_type = request.session['user_type']
        has_access, error_message = check_user_access(user_type, "Staff Log", "create")

        if not has_access:
            return JsonResponse({'message': 'error', 'error_message': error_message})

        form = logForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save(commit=False)
            photo = request.FILES.get('file')
            from_date = request.POST.get('from_date')
            to_date = request.POST.get('to_date')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            project = request.POST.get('project_id')
            task = request.POST.get('task_id')
            status = request.POST.get('task_status')
            task_desc = request.POST.get('task_descriptions')
            issue = request.POST.get('issue_descriptions')

            if employee.is_supervisor == 1:
                category.is_approved = 1
                category.approved_by = user_id
            else:
                category.is_approved = 0
                category.approved_by = 0

            category.file = photo
            category.project_id = project
            category.company_id = company_id
            category.task_id = task
            category.staff_id = user_id
            category.start_date = from_date
            category.to_date = to_date
            category.start_time = start_time
            category.end_time = end_time
            category.task_descriptions = task_desc
            category.issue_descriptions = issue
            category.task_status = status


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
        form = logForm()
    return render(request, 'masters/category.html', {'form': form})


def log_view(request):
    user_type = request.session.get('user_type')
    user_id = request.session.get('user_id')
    company_id = request.session.get('company_id')
    has_access, error_message = check_user_access(user_type, "Staff Log", "read")

    if not has_access:
        return JsonResponse({'data': [], 'message': 'error', 'error_message': error_message})

    project_id = request.POST.get('project')
    task_id = request.POST.get('task')
    log_status = request.POST.get('status')
    from_date = request.POST.get('from_date')
    to_date = request.POST.get('to_date')
    print('project_id',project_id)
    print('task_id',task_id)
    print('log_status',log_status)
    print('from_date',from_date)
    print('to_date',to_date)

    query = Q(status=1,staff_id=user_id, company_id=company_id)


    
    if project_id and project_id.isdigit():
        query &= Q(project_id = project_id)

    if task_id and task_id.isdigit():
        query &= Q(task_id = task_id)

    if log_status:
        query &= Q(task_status=log_status)

    if from_date and to_date:
        query &= Q(start_date__range=[from_date, to_date])



    data = list(log_table.objects.filter(query ).order_by('-id').values()) 

    formatted = []
    for index, item in enumerate(data):

        action_buttons = [
            f'<button type="button" onclick="log_delete(\'{item["id"]}\')" class="btn btn-outline-danger btn-xs" title="Delete"><i class="bx bxs-trash"></i></button>'          
        ]
        
        if item["is_approved"] != 1:  
            edit_button = f'<button type="button" onclick="log_edit(\'{item["id"]}\')" class="btn btn-outline-primary btn-xs" title="Edit"><i class="bx bxs-edit"></i></button>'
            action_buttons.append(edit_button)

        # Always show the delete button
        action_buttons_str = ' '.join(action_buttons)

        # Add data to the formatted response
        formatted.append({
            'id': index + 1,
            'action': action_buttons_str,
            'from': item['start_date'] if item['start_date'] else '-',
            'to': item['to_date'] if item['to_date'] else '-',
            'start': item['start_time'] if item['start_time'] else '-',
            'end': item['end_time'] if item['end_time'] else '-',
            'project': getItemNameById(project_table, item['project_id']) if item['project_id'] else '-',
            'task': getItemNameById(task_table, item['task_id']) if item['task_id'] else '-',
            'desc': item['task_descriptions'] if item['task_descriptions'] else '-',
            'issue': item['issue_descriptions'] if item['issue_descriptions'] else '-',
            'approve': '<span class="badge bg-success">Approved</span>' if item["is_approved"] else '<span class="badge bg-danger">Pending</span>',
            'status': get_task_status_badge(item['task_status']),
        })

    return JsonResponse({'data': formatted})





def get_task_status_badge(task_status):
    """Returns a badge with a color based on task status."""
    badges = {
        'pending': '<span class="badge bg-warning text-dark">Pending</span>',
        'in_progress': '<span class="badge bg-info text-dark">In Progress</span>',
        'completed': '<span class="badge bg-success">Completed</span>',
        'on_hold': '<span class="badge bg-secondary">On Hold</span>',
        'failed': '<span class="badge bg-danger">Failed</span>',
    }
    # Default to 'Pending' if the status is unknown
    return badges.get(task_status, '<span class="badge bg-warning text-dark">Pending</span>')




def log_edit(request):
    if request.method == "POST" and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        frm = request.POST
    data = log_table.objects.filter(id=request.POST.get('id'))    
    return JsonResponse(data.values()[0])




def log_update(request):
    if request.method == "POST":
        category_id = request.POST.get('id')
        category = log_table.objects.get(id=category_id)
        form = logForm(request.POST, request.FILES, instance=category)
        user_type = request.session.get('user_type')
        user_id = request.session.get('user_id')
        print('user_id',user_id)
        company_id = request.session.get('company_id')
        has_access, error_message = check_user_access(user_type, "Staff log", "update")

        if not has_access:
            return JsonResponse({'message': 'error', 'error_message': error_message})

        form = logForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            category = form.save(commit=False)
            photo = request.FILES.get('file')
            from_date = request.POST.get('from_date')
            to_date = request.POST.get('to_date')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            project = request.POST.get('project_id')
            task = request.POST.get('task_id')
            status = request.POST.get('task_status')
            task_desc = request.POST.get('task_descriptions')
            issue = request.POST.get('issue_descriptions')

            if photo:
                category.file = photo


            category.file = photo
            category.project_id = project
            category.company_id = company_id
            category.task_id = task
            category.staff_id = user_id
            category.start_date = from_date
            category.to_date = to_date
            category.start_time = start_time
            category.end_time = end_time
            category.task_descriptions = task_desc
            category.issue_descriptions = issue
            category.task_status = status
            category.updated_by = user_id
            category.updated_on = timezone.now()
            form.save()            
            return JsonResponse({'message': 'success'})
        else:
            errors = form.errors.as_json()
            return JsonResponse({'message': 'error', 'errors': errors})
        

def staff_update(request):
    if request.method == "POST":
        category_id = request.POST.get('id')
        category = log_table.objects.get(id=category_id)
        form = logForm(request.POST, request.FILES, instance=category)
        user_type = request.session.get('user_type')
        user_id = request.session.get('user_id')
        print('user_id',user_id)
        company_id = request.session.get('company_id')
        has_access, error_message = check_user_access(user_type, "Staff log", "update")

        if not has_access:
            return JsonResponse({'message': 'error', 'error_message': error_message})

        form = logForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            category = form.save(commit=False)
            photo = request.FILES.get('file')
            from_date = request.POST.get('from_date')
            to_date = request.POST.get('to_date')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            project = request.POST.get('project_id')
            task = request.POST.get('task_id')
            status = request.POST.get('task_status')
            task_desc = request.POST.get('task_descriptions')
            issue = request.POST.get('issue_descriptions')
            if photo:
                category.file = photo

            category.file = photo
            category.project_id = project
            category.company_id = company_id
            category.task_id = task
            category.start_date = from_date
            category.to_date = to_date
            category.start_time = start_time
            category.end_time = end_time
            category.task_descriptions = task_desc
            category.issue_descriptions = issue
            category.task_status = status
            category.updated_by = user_id
            category.updated_on = timezone.now()
            form.save()            
            return JsonResponse({'message': 'success'})
        else:
            errors = form.errors.as_json()
            return JsonResponse({'message': 'error', 'errors': errors})