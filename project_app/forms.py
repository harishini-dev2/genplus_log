from django import forms
from project_app.models import *

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = employee_table  
        fields = []  


class companyform(forms.ModelForm):
    class Meta:
        model = company_table
        fields = ['name','prefix','address_line1','address_line2','city','state','country','state_code',
        'gstin','phone','mobile','email','fax','tax_id','contact_person','cp_phone','cp_mobile','cp_email','report_email','opening_balance','latitude','longitude','logo','logo_small',
        'logo_invoice']


class categoryForm(forms.ModelForm):
    class Meta:
        model = category_table  
        fields = ['name','is_active'] 


class taskForm(forms.ModelForm):
    class Meta:
        model = task_table  
        fields = [] 

class logForm(forms.ModelForm):
    class Meta:
        model = log_table  
        fields = [] 

class fileForm(forms.ModelForm):
    class Meta:
        model = file_table  
        fields = [] 