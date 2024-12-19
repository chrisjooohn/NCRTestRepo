from django import forms
from django.forms import HiddenInput, CharField
from .models import Dept, Project, Employee
from collections import namedtuple
from django.forms.widgets import Select

CLASSIFICATION_CHOICES = [
    ('1', 'Minor'),
    ('2', 'Major'),
]

SOURCE_CHOICES = [
    ('1', 'Job  '),
    ('2', 'Audit  '),
    ('3', 'Customer  '),
    ('4', 'Management Review  '),
    ('5', 'Others  '),
]

PROGRESS_CHOICES = [
    ('A', 'A. Nonconformance detail description'),
    ('B', 'B. Immediate Correction'),
    ('C', 'C. Root Cause Analysis'),
    ('D', 'D. Corrective Action to the cause'),
    ('E', 'E. Result of action'),
    ('F', 'F. Show Effectiveness'),
    ('G', 'Request For Cancellation'),
]

LIKE_CHOICES = [    
    ('1', 'starts with'),
    ('2', 'contains'),
    ('3', 'ends with'),
]

CA_NECESSARY_CHOICES = [    
    ('1', 'Yes, Proceed to D'),
    ('0', 'No'),    
]

ACTION_EFFECTIVE_CHOICES = [    
    ('1', 'Yes proceed to F'),
    ('0', 'No, Return to C'),  
    ('2', 'For follow-up on date' ), 
]




YES_NO = [    
    ('1', 'Yes'),
    
    
#Start of modify for additional request Edric Marinas 2024/02/26
    #('0', 'No'), 
    
    ('0', ''),   
    #End of modify for additional request Edric Marinas 2024/02/26
]




STATUS = [    
    ('', '---------'),          
    ('1', 'Issued'),
    ('2', 'Cancelled'), 
    ('3', 'Accepted'),    
    ('4', 'On-going'),    
    ('5', 'Closed'),    
    ('6', 'Delayed'),    
    
    
    #Start modifying for additional request Edric Marinas 2024/04/04 
    ('7', 'Cancel Request'), 
    #End modifying for additional request Edric Marinas 2024/04/04
]


ADVANCE_USERS = [    
    ('', '---------'),
    ('1', 'Checker'),
    ('2', 'SH'),    
    ('3', 'Grp-Mgr'),    
    ('5', 'Admin'),        
]

    
#NCOA01 Form       
class NCRCreateForm(forms.Form):    
    
    
    #Edric
    S_or_SN = CharField(widget=HiddenInput(
        attrs={'class': 'form-control', 'id':'S_or_SN'}), 
        required=False) 

    
    
    #Start adding for additional request Edric Marinas 2024/04/04
    hidden_request_cancel = CharField(widget=HiddenInput(attrs={'class': 'form-control', 'id':'hidden_request_cancel'}), 
        required=False) 
    
    hidden_cancel_reason = CharField(widget=HiddenInput(attrs={'class': 'form-control', 'id':'hidden_cancel_reason'}), 
        required=False) 
    
    ncr_no = CharField(widget=HiddenInput(), required=False)
    rev_no = CharField(widget=HiddenInput(
        attrs={'class': 'form-control', 'id':'rev_no'}), 
        required=False) 
    ncr_issue_date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id':'ncr_issue_date', 'placeholder': 'yyyy-MM-dd'}),
        required=False, help_text="Enter Issue Date.")
    dept = forms.ModelChoiceField(
        required=False, label='Section: ', 
        #queryset=Dept.objects.all(),  
        queryset=Dept.objects.all().order_by('name'),
        empty_label="-------------")
    project = forms.ModelChoiceField(
        required=False, 
        label='Project: ', 
        #queryset=Project.objects.none())
        queryset=Project.objects.none().order_by('name'))
    source = forms.ChoiceField(
        widget=forms.RadioSelect(attrs={'class': 'form-control radio-inline', 'id':'source'}),
        required=False, 
        label='Source: ', 
        choices=SOURCE_CHOICES)
    other_source = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id':'other_source'}),
        required=False, label='Others: ', max_length=15) 
    classification = forms.ChoiceField(
        widget=forms.RadioSelect(attrs={'class': 'form-control radio-inline', 'id':'classification'}),
        required=False, 
        label='Classification: ', 
        choices=CLASSIFICATION_CHOICES)
    nc_detail_description = forms.CharField(required=False,
        widget=forms.Textarea(attrs={'cols': '75', 'rows': '7', 'class': 'form-control', 'id':'nc_detail_description', 'placeholder': '-- Please input details for your nonconformance description here... --'}),
        label='A. NC Detail Description : ',
        help_text='Write your message here!',
        max_length=500)


    #EdricEmail
    nc_discoverer_email = forms.EmailField(
        widget=forms.TextInput(attrs={ 'list':'browsers' ,'class': 'form-control', 'id':'nc_discoverer_email', 'size':10}),
        required=False,label='Email: ', max_length=40)    


    nc_discovered_by = forms.CharField(
        widget=forms.TextInput(attrs={ 'class': 'form-control', 'id':'nc_discovered_by','size':10}),
        required=False, label='Staff: ', max_length=40)     
    
    nc_conformed_by = forms.ModelChoiceField(
        required=False, 
        label='SH: ',
        queryset=Employee.objects.all())
    nc_conformed_date = forms.DateField(
        widget=forms.TextInput(attrs={ 'class': 'form-control', 'id':'nc_conformed_date', 'readonly':'readonly', 'size':10}),
        required=False, 
        label='Date: ',
        help_text="Enter NC Comformed Date.")
    ic_description = forms.CharField(required=False,
        widget=forms.Textarea(attrs={'cols': '75', 'rows': '4', 'class': 'form-control', 'id':'ic_description', 'placeholder': '-- Please input details for your immediate correction here... --'}),
        label='B. Immediate Correction : ',
        help_text='Write your message here!',    
        max_length=300)    
    ic_incharge = forms.ModelChoiceField(
        required=False, 
        label='In-Charge: ',
        queryset=Employee.objects.all())
    ic_create_date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id':'ic_create_date', 'readonly':'readonly', 'size':10}),
        required=False, 
        label='Date: ',
        help_text="Enter IC Create Date.")
    ic_approve_by = forms.ModelChoiceField(
        required=False, 
        label='SH: ',
        queryset=Employee.objects.all())    
    ic_approve_date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id':'ic_approve_date', 'readonly':'readonly', 'size':10}),
        required=False, help_text="Enter IC Approved Date.")
    rca_description = forms.CharField(required=False,
        widget=forms.Textarea(attrs={'cols': '75', 'rows': '10', 'class': 'form-control', 'id':'rca_description', 'placeholder': '-- Please input details for your root cause analysis here... --'}),
        label='C. Root Cause Analysis : ',
        help_text='Write your message here!',    
        max_length=750)
    ca_necessary = forms.ChoiceField(
        widget=forms.RadioSelect(attrs={'class': 'form-control radio-inline', 'id':'ca_necessary'}),
        required=False, 
        label='Corrective Action Necessary: ', 
        choices=CA_NECESSARY_CHOICES)
    rca_incharge = forms.ModelChoiceField(
        disabled=True, 
        required=False, 
        label='In-Charge: ',
        queryset=Employee.objects.all())
    rca_create_date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id':'rca_create_date', 'readonly':'readonly', 'size':10}),
        required=False, help_text="Enter RCA Create Date.")
    rca_approve_by = forms.ModelChoiceField(
        required=False, 
        label='Approved By: ',
        queryset=Employee.objects.all())
    rca_approve_date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id':'rca_approve_date', 'readonly':'readonly', 'size':10}),
        required=False, help_text="Enter RCA Approve Date.")
    ca_description = forms.CharField(required=False,
        widget=forms.Textarea(attrs={'cols': '75', 'rows': '4', 'class': 'form-control', 'id':'ca_description', 'placeholder': '-- Please input details for your corrective action to the cause here... --'}),
        label='D. Corrective Action :',
        help_text='Write your message here!',    
        max_length=300)
    ca_target_date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id':'ca_target_date', 'placeholder': 'yyyy-MM-dd'}),
        required=False, 
        label='Target Date Of Accomplishment: ',
        help_text="Enter Target Date.")
    ca_checked_by_sh = forms.ModelChoiceField(
        required=False, 
        label='SH: ',
        queryset=Employee.objects.all())
    ca_check_date_by_sh = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id':'ca_check_date_by_sh', 'readonly':'readonly', 'size':10}),
        label='Date: ',
        required=False, help_text="Enter IC Create Date.")
    ca_approved_by_mgr = forms.ModelChoiceField(
        required=False, 
        label='Grp Mgr: ',
        queryset=Employee.objects.all())
    ca_approved_date_by_mgr = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id':'ca_approved_date_by_mgr', 'readonly':'readonly', 'size':10}),
        required=False,
        label='Date: ')
    ra_description = forms.CharField(required=False,
        widget=forms.Textarea(attrs={'cols': '75', 'rows': '4', 'class': 'form-control', 'id':'ra_description', 'placeholder': '-- Please input details for your result of action here... --'}),
        label='E. Result Action : ',
        help_text='Write your message here!',    
        max_length=300)
    ra_action_effective = forms.ChoiceField(
        widget=forms.RadioSelect(attrs={'class': 'form-control radio-inline', 'id':'ra_action_effective'}),
        required=False, 
        label='Action Effective : ', 
        choices=ACTION_EFFECTIVE_CHOICES)
    ra_followup_date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id':'ra_followup_date'}),
        required=False,
        label='Date: ')
    ra_check_by_staff = forms.ModelChoiceField(
        disabled=True, 
        required=False, 
        label='In-Charge: ',
        queryset=Employee.objects.all())
    ra_check_date_by_staff = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id':'ra_check_date_by_staff', 'readonly':'readonly', 'size':10}),
        required=False,
        label='Date: ')
    ra_check_by_sh = forms.ModelChoiceField(
        required=False, 
        label='SH: ',
        queryset=Employee.objects.all())
    ra_check_date_by_sh = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id':'ra_check_date_by_sh', 'readonly':'readonly', 'size':10}),
        required=False,
        label='Date: ')
    se_description = forms.CharField(required=False,
        widget=forms.Textarea(attrs={'cols': '75', 'rows': '4', 'class': 'form-control', 'id':'se_description', 'placeholder': '-- Please input details for your effectiveness here... --'}),
        label='F. Show Effectiveness : ',
        help_text='Write your message here!',    
        max_length=300)    
    
    #EDRIC
    #se_ro_updated = forms.ChoiceField(
    #    widget=forms.RadioSelect(attrs={'class': 'form-control radio-inline', 'id':'se_ro_updated'}),
    #    required=False, 
    #    label='RO Updated? ', 
    #    choices=YES_NO)
    
    
    se_ro_updated = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-control radio-inline', 'id':'se_ro_updated'}),
        required=False, 
        label='RO Updated? ',
        choices=YES_NO)
    
    
    se_check_by_mgr = forms.ModelChoiceField(
        required=False, 
        label='Grp Mgr: ',
        queryset=Employee.objects.all())
    se_check_date_by_mgr = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id':'se_check_date_by_mgr', 'readonly':'readonly', 'size':10}),
        required=False,
        label='Date: ')
    se_check_by_qa = forms.ModelChoiceField(
        required=False, 
        label='QA Mgr: ',
        queryset=Employee.objects.all())
    se_check_date_by_qa = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id':'se_check_date_by_qa', 'readonly':'readonly', 'size':10}),
        required=False,
        label='Date: ')
    status = CharField(widget=HiddenInput(
        attrs={'id':'status'}),      
        required=False) 
    comments = forms.CharField(required=False,
        widget=forms.Textarea(attrs={'cols': '100', 'rows': '4', 'class': 'form-control', 'id':'comments', 'placeholder': '-- Please input details for your comments here... --'}),
        label='Comments: ',
        help_text='Write your comments here!',    
        max_length=1000)   
    
    
    hidden_dept_id = CharField(widget=HiddenInput(attrs={'class': 'form-control', 'id':'hidden_dept_id'}), 
        required=False) 
    
    hidden_update_date = CharField(widget=HiddenInput(attrs={'class': 'form-control', 'id':'hidden_update_date'}), 
        required=False) 
    
    

    nc_conforme_status = CharField(widget=HiddenInput(
        attrs={'class': 'form-control', 'id':'nc_conforme_status'}), 
        required=False) 
    ic_approve_status = CharField(widget=HiddenInput(
        attrs={'class': 'form-control', 'id':'ic_approve_status'}), 
        required=False) 
    rca_approve_status = CharField(widget=HiddenInput(
        attrs={'class': 'form-control', 'id':'rca_approve_status'}), 
        required=False) 
    ca_check_by_sh_status = CharField(widget=HiddenInput(
        attrs={'class': 'form-control', 'id':'ca_check_by_sh_status'}), 
        required=False) 
    ca_approve_by_mgr_status = CharField(widget=HiddenInput(
        attrs={'class': 'form-control', 'id':'ca_approve_by_mgr_status'}), 
        required=False) 
    ra_check_by_sh_status = CharField(widget=HiddenInput(
        attrs={'class': 'form-control', 'id':'ra_check_by_sh_status'}), 
        required=False) 
    se_check_by_mgr_status = CharField(widget=HiddenInput(
        attrs={'class': 'form-control', 'id':'se_check_by_mgr_status'}), 
        required=False) 
    se_check_by_qa_status = CharField(widget=HiddenInput(
        attrs={'class': 'form-control', 'id':'se_check_by_qa_status'}), 
        required=False) 
    
    process = CharField(widget=HiddenInput(
        attrs={'class': 'form-control', 'id':'process'}), 
        required=False) 
    
    reason_action_not_effective = CharField(widget=HiddenInput(
        attrs={'id':'reason_action_not_effective'}), 
        required=False) 
    
    is_A_on_edit_mode = CharField(widget=HiddenInput(
        attrs={'id':'is_A_on_edit_mode'}), 
        required=False) 
    is_B_on_edit_mode = CharField(widget=HiddenInput(
        attrs={'id':'is_B_on_edit_mode'}), 
        required=False) 
    is_C_on_edit_mode = CharField(widget=HiddenInput(
        attrs={'id':'is_C_on_edit_mode'}), 
        required=False) 
    is_D_on_edit_mode = CharField(widget=HiddenInput(
        attrs={'id':'is_D_on_edit_mode'}), 
        required=False) 
    is_E_on_edit_mode = CharField(widget=HiddenInput(
        attrs={'id':'is_E_on_edit_mode'}), 
        required=False) 
    is_F_on_edit_mode = CharField(widget=HiddenInput(
        attrs={'id':'is_F_on_edit_mode'}), 
        required=False) 
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['project'].queryset = Project.objects.none()
    
        if 'dept' in self.data:
            try:
                dept_id = int(self.data.get('dept'))
                
                self.fields['project'].queryset = Project.objects.filter(dept_id=dept_id).order_by('name')
                
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty Project queryset
        
        self.fields['ncr_issue_date'].widget.attrs['size'] = 10 
        self.fields['ca_target_date'].widget.attrs['size'] = 10 
        self.fields['ra_followup_date'].widget.attrs['size'] = 10 
        self.fields['nc_discovered_by'].widget.attrs['size'] = 40 
        
        
        #EdricEmail
        self.fields['nc_discoverer_email'].widget.attrs['size'] = 40 
        
        
        
        self.fields['dept'].widget.attrs['class'] = 'form-control'
        self.fields['project'].widget.attrs['class'] = 'form-control'
        
        self.fields['nc_conformed_by'].widget.attrs['class'] = 'form-control'
        self.fields['ca_approved_by_mgr'].widget.attrs['class'] = 'form-control'
        self.fields['se_check_by_qa'].widget.attrs['class'] = 'form-control'
        
        self.fields['nc_conformed_by'].widget.attrs['id'] = 'nc_conformed_by'
        self.fields['ca_approved_by_mgr'].widget.attrs['id'] = 'ca_approved_by_mgr'
        self.fields['se_check_by_qa'].widget.attrs['id'] = 'se_check_by_qa'
        
        self.fields['rca_incharge'].widget.attrs['class'] = 'form-control'
        self.fields['rca_incharge'].widget.attrs['id'] = 'rca_incharge'
        
        self.fields['ra_check_by_staff'].widget.attrs['class'] = 'form-control'
        self.fields['ra_check_by_staff'].widget.attrs['id'] = 'ra_check_by_staff'
        
        self.fields['ic_incharge'].widget.attrs['class'] = 'form-control'
        self.fields['ic_incharge'].widget.attrs['id'] = 'ic_incharge'
        
        self.fields['ic_approve_by'].widget.attrs['class'] = 'form-control'
        self.fields['ic_approve_by'].widget.attrs['id'] = 'ic_approve_by'
        
        self.fields['rca_approve_by'].widget.attrs['class'] = 'form-control'
        self.fields['rca_approve_by'].widget.attrs['id'] = 'rca_approve_by'
        
        self.fields['ca_checked_by_sh'].widget.attrs['class'] = 'form-control'
        self.fields['ca_checked_by_sh'].widget.attrs['id'] = 'ca_checked_by_sh'
        
        self.fields['ra_check_by_sh'].widget.attrs['class'] = 'form-control'
        self.fields['ra_check_by_sh'].widget.attrs['id'] = 'ra_check_by_sh'
        
        self.fields['se_check_by_mgr'].widget.attrs['class'] = 'form-control'
        self.fields['se_check_by_mgr'].widget.attrs['id'] = 'se_check_by_mgr'
  
        
  
class NCRVerifyForm(forms.Form):
    source = forms.ChoiceField(
        disabled=True, 
        widget=forms.RadioSelect(attrs={'style': 'display: inline-block'}),
        required=False, 
        label='Source : ',
        choices=SOURCE_CHOICES)
    classification = forms.ChoiceField(
        disabled=True,
        widget=forms.RadioSelect(attrs={'class': 'inline',  'id':'classification'}),
        required=False, 
        label='Classification : ', 
        choices=CLASSIFICATION_CHOICES)    
    ic_incharge = forms.ModelChoiceField(
        required=False, 
        label='In-Charge: ',
        queryset=Employee.objects.all())
    ca_necessary = forms.ChoiceField(
        disabled=True, 
        widget=forms.RadioSelect(attrs={'class': 'form-control radio-inline', }),
        required=False, 
        label='Corrective Action Necessary : ', 
        choices=CA_NECESSARY_CHOICES)
    ra_action_effective = forms.ChoiceField(
        disabled=True, 
        widget=forms.RadioSelect(attrs={'class': 'form-control radio-inline', 'id':'ra_action_effective'}),
        required=False, 
        label='Action Effective : ', 
        choices=ACTION_EFFECTIVE_CHOICES)
    
    
    #EDRIC
    #se_ro_updated = forms.ChoiceField(
    #    disabled=True, 
    #    widget=forms.RadioSelect(attrs={'class': 'form-control radio-inline', 'id':'se_ro_updated'}),
    #    required=False, 
    #    label='RO Updated? ', 
    #    choices=YES_NO)
    
    
    se_ro_updated = forms.MultipleChoiceField(
        disabled=True, 
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-control radio-inline', 'id':'se_ro_updated'}),
        required=False, 
        label='RO Updated? ',
        choices=YES_NO)

    

    hidden_process = CharField(widget=HiddenInput(attrs={'class': 'form-control', 'id':'hidden_process'}), 
        required=False) 
    hidden_update_date = CharField(widget=HiddenInput(attrs={'class': 'form-control', 'id':'hidden_update_date'}), 
        required=False) 
    
    current_datetime = CharField(widget=HiddenInput(attrs={'type':'text','class': 'form-control', 'id':'current_datetime'}), 
        required=False) 


#NCOA03 Form   
class NCRSearchForm(forms.Form):
    ncr_no = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id':'ncr_no'}),
        label='NCR#: ', 
        max_length=30)     
    project = forms.ModelChoiceField(
        queryset=Project.objects.none(),
        label='Project: ', )
    dept = forms.ModelChoiceField(
        queryset=Dept.objects.all(),
        label='Section: ', )
    ic_incharge = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id':'ic_incharge'}),
        label='In-Charge: ', 
        max_length=30) 
    classification = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=CLASSIFICATION_CHOICES,
        label='Classification: ',)
    progress = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=PROGRESS_CHOICES,
        label='Progress: ',)
    ncr_no_like_cond = forms.ChoiceField(required=False,choices=LIKE_CHOICES)
    ic_incharge_like_cond = forms.ChoiceField(required=False,choices=LIKE_CHOICES)
    status = CharField(
        required=False, 
        widget=Select(attrs={'class': 'form-control', 'id':'status'}, choices=STATUS),
        label='Status: ')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['project'].queryset = Project.objects.none()
    
        if 'dept' in self.data:
            try:
                dept_id = int(self.data.get('dept'))
                self.fields['project'].queryset = Project.objects.filter(dept_id=dept_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty Project queryset
        
        self.fields['dept'].widget.attrs['class'] = "form-control"
        self.fields['project'].widget.attrs['class'] = "form-control"
        self.fields['dept'].widget.attrs['class'] = "form-control"
        self.fields['ncr_no_like_cond'].widget.attrs['class'] = "form-control"
        self.fields['ic_incharge_like_cond'].widget.attrs['class'] = "form-control"
        self.fields['progress'].widget.attrs['class'] = "form-control"
        self.fields['classification'].widget.attrs['class'] = "form-control"
        self.fields['ncr_no'].widget.attrs['size'] = 40 
        self.fields['ic_incharge'].widget.attrs['size'] = 40 
        
        self.fields['dept'].widget.attrs['id'] = "dept"
        
        
        
        
    
    
#NCOA04
class LoginForm(forms.Form):
    chapano = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'id':'chapano', 'placeholder':'Enter your chapaNo', 'size':20}),
        label='ChapaNo: ', 
        max_length=30)     
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={'class':'form-control', 'type':'password', 'align':'center', 'placeholder':'Enter your password', 'size':20}),)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



class ProjectForm(forms.Form):
    project_id = CharField(
        widget=HiddenInput(attrs={'class': 'form-control', 'id':'project_id'}), 
        required=False) 
    dept = forms.ModelChoiceField(
        label='Section: ', 
        queryset=Dept.objects.all().order_by('-name'),  
        empty_label="-------------")
    code = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id':'code'}),
        label='Code: ', 
        max_length=20,
        required=False)  
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id':'name'}),
        label='Name: ', 
        max_length=30,
        required=False)
    archive_location = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'id':'archive_location'}),
        label='Archive Location: ', 
        max_length=50,)  
    insert_id = CharField(
        widget=HiddenInput(attrs={'class': 'form-control', 'id':'insert_id'}), 
        required=False) 
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dept'].widget.attrs['class'] = "form-control"
        self.fields['code'].widget.attrs['size'] = 30 
        self.fields['name'].widget.attrs['size'] = 40 
        self.fields['archive_location'].widget.attrs['size'] = 50 
  
        
  
class ProjectUForm(forms.Form):
    project_id = CharField(
        widget=HiddenInput(attrs={'class': 'form-control', 'id':'project_id'}), 
        required=False) 
    dept = forms.ModelChoiceField(
        required=False,
        label='Section: ', 
        queryset=Dept.objects.all().order_by('-name'),
        empty_label="-------------")
    code = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id':'code'}),
        label='Code: ', 
        max_length=20)  
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id':'name'}),
        label='Name: ', 
        max_length=30)
    archive_location = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'id':'archive_location'}),
        label='Archive Location: ', 
        max_length=50)  
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dept'].widget.attrs['class'] = "form-control"
        self.fields['code'].widget.attrs['size'] = 30 
        self.fields['name'].widget.attrs['size'] = 40 
        self.fields['archive_location'].widget.attrs['size'] = 50 

        
        
class EmployeePasswordForm(forms.Form):
    currentPassword = forms.CharField(
        label="Current Password: ",
        widget=forms.PasswordInput(
            attrs={'class':'form-control', 'type':'password', 'align':'center', 'placeholder':'Enter your current password', 'size':25, 'maxlength':15}),
        )
    newPassword = forms.CharField(
        label="New Password: ",
        widget=forms.PasswordInput(
            attrs={'class':'form-control', 'type':'password', 'align':'center', 'placeholder':'Enter your new password', 'size':25, 'maxlength':15}),
        )
    confirmPassword = forms.CharField(
        label="Confirm Password: ",
        widget=forms.PasswordInput(
            attrs={'class':'form-control', 'type':'password', 'align':'center', 'placeholder':'Enter your confirm password', 'size':25, 'maxlength':15}),    
        )
     
    
    
def namedtuplefetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]




        
        
        