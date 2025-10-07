from django.contrib import admin
from django.urls import path
from project_app import views,staff


urlpatterns = [


    path('',views.signin),

    path('signin',views.signin),

    path('admin',views.admin),

    path('login/',views.login),

    path('login_admin/',views.login_admin),

    path('logout',views.logout),

    path('dashboard',views.dashboard),

    
    path('company',views.company),
    path('company_add',views.company_add),
    path('company_edit/',views.company_edit),
    path('update_company/',views.update_company),
    path('add_company_details/',views.add_company_details),
    path('company_report/',views.company_report),
    path('company_delete/',views.company_delete),
    path('fetch_technicians/',views.fetch_technicians),
    path('company/admin',views.company_edits),



    path('employee',views.employee),
    path('employee_view/',views.employee_view),
    path('employee_add/',views.employee_add),
    path('employee_edit/',views.employee_edit),
    path('employee_update/',views.employee_update),
    path('employee_delete/',views.employee_delete),
    path('employee_report/',views.employee_report),

    path('user_privilege',views.user_privilege),
    path('get_roles/',views.get_roles),
    path('view_roles/',views.view_roles),
    path('add_roles/',views.add_roles),
    path('privileges_update/',views.privileges_update),
    path('edit_roles/',views.edit_roles),    
    path('update_roles/',views.update_roles),
    path('duplicate_add/',views.duplicate_add),
    path('role_duplicate/',views.role_duplicate),    
    path('delete_roles/',views.delete_roles),
    path('refresh_privileges/',views.refresh_privileges),

    path('category',views.category),
    path('category_add/',views.category_add),
    path('category_view/',views.category_view),
    path('category_edit/',views.category_edit),
    path('category_update/',views.category_update),
    path('category_delete/',views.category_delete),
    
    path('customer',views.customer),
    path('customer_add/',views.customer_add),
    path('customer_view/',views.customer_view),
    path('customer_edit/',views.customer_edit),
    path('customer_update/',views.customer_update),
    path('customer_delete/',views.customer_delete),

    path('project',views.project),
    path('project_add/',views.project_add),
    path('project_view/',views.project_view),
    path('project_edit/',views.project_edit),
    path('project_update/',views.project_update),
    path('project_delete/',views.project_delete),

    path('load_task_tab/',views.load_task_tab),

    path('log_details/',views.log_details),

    

    path('task',views.task),
    path('fetch_task/<int:project_id>/',views.fetch_task, name='fetch_task'),
    path('task_add/',views.task_add),
    path('task_view/',views.task_view),
    path('task_edit/',views.task_edit),
    path('task_update/',views.task_update),
    path('task_delete/',views.task_delete),

    path('staff_log',views.staff_log),
    path('staff_log_view/',views.staff_log_view),
    path('log_approval/',views.log_approval),
    path('log_delete/',views.log_delete),

    path('dates_add/',views.dates_add),
    path('dates_view/',views.dates_view),
    path('dates_delete/',views.dates_delete),
    path('dates_edit/',views.dates_edit),
    path('date_update/',views.date_update),


    path('files_add/',views.files_add),
    path('file_view/',views.file_view),
    path('file_edit/',views.file_edit),
    path('file_update/',views.file_update),
    path('file_delete/',views.file_delete),
    


    path('call_add/',views.call_add),
    path('call_view/',views.call_view),
    path('call_edit/',views.call_edit),
    path('call_update/',views.call_update),
    path('call_delete/',views.call_delete),

    path('notes_add/',views.notes_add),
    path('notes_view/',views.notes_view),
    path('notes_edit/',views.notes_edit),
    path('notes_update/',views.notes_update),
    path('notes_delete/',views.notes_delete),


    path('credentials_add/',views.credentials_add),
    path('credentials_view/',views.credentials_view),
    path('credentials_edit/',views.credentials_edit),
    path('credentials_update/',views.credentials_update),
    path('credentials_delete/',views.credentials_delete),


    path('create_todo/', views.create_todo, name='create_todo'),
    path('get_todo_list/', views.get_todo_list, name='get_todo_list'),
    path('toggle_status/', views.toggle_status, name='toggle_status'),
    path('delete_todo/',views.delete_todo),

    path('staff/dashboard',staff.staff_dashboard),
    path('staff/log_entry',staff.log_entry),
    path('staff_projects/', staff.fetch_projects, name='fetch_projects'),
    path('staff_task/<int:project_id>/', staff.fetch_tasks, name='fetch_tasks'),
    path('log_add/',staff.log_add),
    path('log_view/',staff.log_view),
    path('log_edit/',staff.log_edit),
    path('log_update/',staff.log_update),
    path('staff_update/',staff.staff_update),

   ]