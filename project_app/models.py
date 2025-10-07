from django.db import models


class employee_table(models.Model):
    employee_code = models.CharField(max_length=15, unique=True,)
    employee_role = models.CharField(max_length=50,blank=True, null=True)
    user_role = models.CharField(max_length=50,blank=True, null=True)
    name = models.CharField(max_length=150)
    username = models.CharField(max_length=150)
    finger_print = models.CharField(max_length=150,blank=True, null=True)
    address_line1 = models.CharField(max_length=150,blank=True, null=True)
    address_line2 = models.CharField(max_length=150, blank=True, null=True)
    password = models.CharField(max_length=50)
    country = models.CharField(max_length=50,blank=True, null=True)
    city = models.CharField(max_length=50,blank=True, null=True)
    postal_code = models.CharField(max_length=50,blank=True, null=True)
    phone = models.CharField(max_length=15)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(max_length=255)
    certificate = models.FileField(upload_to='', max_length=300, blank=True, null=True)
    is_superadmin = models.BooleanField(default=False)
    is_scheduler = models.BooleanField(default=False)
    is_technician = models.BooleanField(default=False)
    is_supervisor = models.BooleanField(default=False)
    is_foreigner = models.BooleanField(default=False)
    is_gps = models.BooleanField(default=False)
    is_photo = models.BooleanField(default=False)
    is_qr = models.BooleanField(default=False)
    is_signature = models.BooleanField(default=False)
    vehicle_number = models.CharField(max_length=50)
    color = models.CharField(max_length=7)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    is_admin = models.IntegerField(default=0)
    company_id = models.IntegerField(default=0)
    created_on = models.DateTimeField(blank=True, null=True)
    updated_on = models.DateTimeField(blank=True, null=True)
    created_by = models.IntegerField()
    updated_by = models.IntegerField()
    device_id = models.CharField(max_length=20)
    fcm_token = models.CharField(max_length=100)
    ms_token = models.TextField()
    expires_on = models.DateTimeField(null=True)
    auth_id = models.IntegerField()
    login_from = models.CharField(max_length=50)
    supervisor_id = models.IntegerField(default=0 )
    class Meta:
        db_table = "employee"




class company_table(models.Model):
    name = models.CharField(max_length=150,blank=True, null=True)
    prefix = models.CharField(max_length=10,blank=True, null=True)
    address_line1 = models.CharField(max_length=150,blank=True, null=True)
    address_line2 = models.CharField(max_length=150,blank=True, null=True)
    city = models.CharField(max_length=50,blank=True, null=True)
    state = models.CharField(max_length=50,blank=True, null=True)
    country = models.CharField(max_length=50,blank=True, null=True)
    state_code = models.CharField(max_length=50,blank=True, null=True)
    gstin = models.CharField(max_length=50,blank=True, null=True)
    phone = models.CharField(max_length=15,blank=True, null=True)
    mobile = models.CharField(max_length=15,blank=True, null=True)
    email = models.CharField(max_length=30,blank=True, null=True)
    fax = models.CharField(max_length=30,blank=True, null=True)
    tax_id = models.IntegerField(blank=True, null=True)
    contact_person = models.CharField(max_length=50,blank=True, null=True)
    cp_phone = models.CharField(max_length=15,blank=True, null=True)
    cp_mobile = models.CharField(max_length=15)
    cp_email = models.CharField(max_length=30,blank=True, null=True)
    report_email = models.CharField(max_length=30,blank=True, null=True)
    opening_balance = models.IntegerField(blank=True, null=True)
    latitude = models.CharField(max_length=50,blank=True, null=True)
    longitude = models.CharField(max_length=50,blank=True, null=True)
    logo = models.ImageField(upload_to='images/', max_length=50,blank=True, null=True)
    logo_small = models.ImageField(upload_to='images/', max_length=50,blank=True, null=True)
    logo_invoice = models.ImageField(upload_to='images/', max_length=50,blank=True, null=True)
    company_code = models.CharField(max_length=50)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField(auto_now_add=True)
    updated_on=models.DateTimeField(auto_now_add=True)
    created_by=models.IntegerField()
    updated_by=models.IntegerField()
    primary_technician = models.IntegerField()
    class Meta:
        db_table="company"





class AdminRoles(models.Model):
    name = models.CharField(max_length=150)
    descriptions = models.CharField(max_length=150)
    status = models.IntegerField(default=1)
    is_active = models.IntegerField(default=1)
    created_on = models.DateTimeField()
    updated_on = models.DateTimeField()
    created_by = models.IntegerField()
    updated_by = models.IntegerField()

    class Meta:
        db_table = "admin_roles"


class AdminModules(models.Model):
    name = models.CharField(max_length=150)
    sort_order_no = models.IntegerField()
    is_vendor = models.IntegerField(default=0)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on = models.DateTimeField()
    updated_on = models.DateTimeField()
    created_by = models.IntegerField()
    updated_by = models.IntegerField()

    class Meta:
        db_table = "admin_module"

class AdminPrivilege(models.Model):
    role_id = models.IntegerField()
    module_id = models.IntegerField()
    is_create = models.IntegerField(default=0)
    is_read = models.IntegerField(default=0)
    is_update = models.IntegerField(default=0)
    is_delete = models.IntegerField(default=0)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on = models.DateTimeField()
    updated_on = models.DateTimeField()
    created_by = models.IntegerField()
    updated_by = models.IntegerField()

    class Meta:
        db_table = "admin_privilege"



class category_table(models.Model):
    name = models.CharField(max_length=150)
    image = models.ImageField(upload_to='images/', max_length=300)
    description = models.CharField(max_length=300)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()
    created_by=models.IntegerField()
    updated_by=models.IntegerField()
    class Meta:
        db_table="categories"


class customer_table(models.Model):
    name = models.CharField(max_length=150)
    email = models.CharField(max_length=30)
    mobile = models.CharField(max_length=15)
    address = models.TextField()
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    contact_person = models.CharField(max_length=150)
    cp_mobile = models.CharField(max_length=15)
    cp_phone = models.CharField(max_length=15)
    cp_email = models.CharField(max_length=30)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()
    created_by=models.IntegerField()
    updated_by=models.IntegerField()
    class Meta:
        db_table="customer"


class project_table(models.Model):
    company_id = models.IntegerField()
    category_id = models.IntegerField()
    num_series = models.IntegerField()
    project_code = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    prefix = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    deadline = models.DateField()
    project_value = models.CharField(max_length=100)
    project_incharge = models.IntegerField()
    incharge_email = models.CharField(max_length=30)
    incharge_phone = models.CharField(max_length=15)
    percentage = models.CharField(max_length=5)
    project_status = models.CharField(max_length=50)
    description = models.TextField()
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()
    created_by=models.IntegerField()
    updated_by=models.IntegerField()
    class Meta:
        db_table="projects"





class task_table(models.Model):
    company_id = models.IntegerField()
    num_series=models.CharField(max_length=10)
    task_code = models.CharField(max_length=15)
    project_id = models.IntegerField()
    contribution = models.CharField(max_length=10)
    name = models.CharField(max_length=150)
    staff_id = models.CharField(max_length=10)
    priority = models.CharField(max_length=30,default='normal')
    task_status = models.CharField(max_length=30,default='pending')
    start_date=models.DateField(null=True)
    due_date=models.DateField(null=True)
    file = models.ImageField(upload_to='task/', max_length=150)
    descriptions = models.TextField()
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()
    created_by=models.IntegerField()
    updated_by=models.IntegerField()
    class Meta:
        db_table="task"



class log_table(models.Model):
    project_id = models.IntegerField()
    company_id = models.IntegerField()
    task_id = models.IntegerField()
    staff_id = models.CharField(max_length=10)
    start_date = models.DateField(null=True)
    to_date = models.DateField(null=True)
    start_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)
    file = models.ImageField(upload_to='staff_log/', max_length=150)
    task_descriptions = models.TextField()
    issue_descriptions = models.TextField()
    task_status = models.CharField(max_length=30,default='pending')
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()
    created_by=models.IntegerField()
    updated_by=models.IntegerField()
    is_approved=models.IntegerField(default=0)
    approved_by=models.IntegerField(default=0)
    class Meta:
        db_table="staff_log"



class important_table(models.Model):
    project_id = models.IntegerField()
    task_id = models.IntegerField()
    project_id = models.IntegerField()
    company_id = models.IntegerField()  
    date = models.DateField(null=True)
    name = models.CharField(max_length=150)
    descriptions = models.TextField()  
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()
    created_by=models.IntegerField()
    updated_by=models.IntegerField()    
    class Meta:
        db_table="important_dates"

class credentials_table(models.Model):
    task_id = models.IntegerField()
    project_id = models.IntegerField()
    company_id = models.IntegerField()    
    name = models.CharField(max_length=150)
    username = models.CharField(max_length=150)
    email = models.CharField(max_length=30)
    password = models.CharField(max_length=20)
    descriptions = models.TextField()
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()
    created_by=models.IntegerField()
    updated_by=models.IntegerField()    
    class Meta:
        db_table="credentials"


class notes_table(models.Model):
    task_id = models.IntegerField()
    project_id = models.IntegerField()
    company_id = models.IntegerField()    
    date = models.DateField(null=True)
    title = models.CharField(max_length=150)
    short_descriptions = models.CharField(max_length=200)
    descriptions = models.TextField()
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()
    created_by=models.IntegerField()
    updated_by=models.IntegerField()    
    class Meta:
        db_table="notes"


class file_table(models.Model):
    task_id = models.IntegerField()
    project_id = models.IntegerField()
    company_id = models.IntegerField()    
    name = models.CharField(max_length=150)
    file = models.FileField(upload_to='file_manager/', max_length=300)
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()
    created_by=models.IntegerField()
    updated_by=models.IntegerField()    
    class Meta:
        db_table="file_manager"


class call_table(models.Model):
    task_id = models.IntegerField()
    project_id = models.IntegerField()
    company_id = models.IntegerField()    
    date = models.DateField(null=True)
    time = models.TimeField(null=True)
    call_type = models.CharField(max_length=15)
    contact_person = models.CharField(max_length=100)
    descriptions = models.TextField()
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()
    created_by=models.IntegerField()
    updated_by=models.IntegerField()    
    class Meta:
        db_table="call_log"


class todo_table(models.Model):
    task_id = models.IntegerField()
    project_id = models.IntegerField()
    company_id = models.IntegerField()    
    todo_status = models.CharField(max_length=15)
    name = models.TextField()
    is_active = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    created_on=models.DateTimeField()
    updated_on=models.DateTimeField()
    created_by=models.IntegerField()
    updated_by=models.IntegerField()    
    class Meta:
        db_table="todo"