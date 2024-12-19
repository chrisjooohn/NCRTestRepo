from django.db import models


class Dept(models.Model):
    name = models.TextField(blank=True, null=True)
    groupid = models.CharField(db_column='groupId', max_length=2)  # Field name made lowercase.
    code = models.CharField(db_column='code', blank=True, null=True, max_length=2)
    
    class Meta:
        managed = False
        db_table = 'dept'

    def __str__(self):
        return self.name


class Employee(models.Model):
    chapano = models.CharField(db_column='chapaNo', primary_key=True, max_length=3)  # Field name made lowercase.
    lastname = models.TextField(db_column='lastName', blank=True, null=True)  # Field name made lowercase.
    firstname = models.TextField(db_column='firstName', blank=True, null=True)  # Field name made lowercase.
    middlename = models.TextField(db_column='middleName', blank=True, null=True)  # Field name made lowercase.
    password = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    email = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'employee'



class PositionDetail(models.Model):
    id = models.CharField(primary_key=True, max_length=3)
    positioncd = models.CharField(db_column='positionCd', max_length=3)  # Field name made lowercase.
    positionnm = models.CharField(db_column='positionNm', max_length=50)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'positiondetail'



class Positions(models.Model):
    id = models.CharField(primary_key=True, max_length=3)
    name = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'positions'



class Rank(models.Model):
    chapano = models.CharField(db_column='chapaNo', primary_key=True, max_length=3)  # Field name made lowercase.
    positionid = models.CharField(db_column='positionId', max_length=3)  # Field name made lowercase.
    deptid = models.TextField(db_column='deptId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'rank'
        unique_together = (('chapano', 'positionid'),)
     
        
     
class Project(models.Model):
    #id = models.CharField(primary_key=True, max_length=3)
    dept = models.ForeignKey(Dept, on_delete=models.CASCADE)
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=15, blank=True, null=True)
    archive_location = models.CharField(max_length=50, blank=True, null=True)
    insert_user_id = models.CharField(max_length=6)
    
    class Meta:
        managed = False
        db_table = 'project'
        unique_together = (('dept', 'code', 'name'),)    
        
    def __str__(self):
        return self.name           
        
    
    
# テーブル名:NCR_DETAIL_MSTR
class NcrDetailMstr(models.Model):

    CLASS_CHOICE = (
        ('1', 'Minor'),
        ('2', 'Major'),        
    )

    SOURCE_CHOICE = (
        ('1', 'Job'),
        ('2', 'Audit Finding'),  
        ('3', 'Customer Feedback'), 
        ('4', 'Management Action'), 
        ('5', 'Others'),
    )
    
    YN_CHOICE = (
        ('1', 'Yes'),
        ('0', 'No'),  
    )

    EFFECTIVE_CHOICE = (
        ('1', 'Yes, proceed to F'),
        ('0', 'No, Return to C'), 
        ('2', 'For folow-up on date'), 
    )
     
    ncr_no = models.CharField(max_length=43, primary_key=True)
    rev_no = models.IntegerField(null=True, blank=True)
    ncr_issue_date = models.DateTimeField()
    dept = models.ForeignKey(Dept, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    serial_no = models.CharField(max_length=3)     
    source = models.CharField(null=True, blank=True, max_length=1, choices=SOURCE_CHOICE)
    other_source = models.CharField(max_length=15,null=True, blank=True)
    classification = models.CharField(null=True, blank=True, max_length=1, choices=CLASS_CHOICE)
    nc_detail_description = models.CharField(max_length=200,null=True, blank=True)
    nc_discovered_by = models.CharField(max_length=15,null=True, blank=True)
    nc_conformed_by = models.CharField(max_length=3,null=True, blank=True)
    nc_conformed_date = models.DateTimeField(null=True, blank=True)
    ncr_issue_by = models.CharField(max_length=3,null=True, blank=True)
    ic_description = models.CharField(max_length=200,null=True, blank=True)
    ic_incharge = models.CharField(max_length=3,null=True, blank=True)
    ic_create_date = models.DateTimeField(null=True, blank=True)
    ic_approve_by =  models.CharField(max_length=3,null=True, blank=True)
    ic_approve_date = models.DateTimeField(null=True, blank=True)
    rca_description =  models.CharField(max_length=200,null=True, blank=True)
    ca_necessary = models.CharField(null=True, blank=True, max_length=1, choices=YN_CHOICE)
    rca_incharge = models.CharField(max_length=3,null=True, blank=True)
    rca_create_date = models.DateTimeField(null=True, blank=True)
    rca_approve_by = models.CharField(max_length=3,null=True, blank=True)
    rca_approve_date = models.DateTimeField(null=True, blank=True)
    ca_target_date = models.DateField(null=True, blank=True)
    ca_description = models.CharField(max_length=200,null=True, blank=True)
    ca_create_by = models.CharField(max_length=3,null=True, blank=True)
    ca_create_date = models.DateTimeField(null=True, blank=True)
    ca_checked_by_sh = models.CharField(max_length=3,null=True, blank=True)
    ca_check_date_by_sh = models.DateTimeField(null=True, blank=True)
    ca_approved_by_mgr = models.CharField(max_length=3,null=True, blank=True)
    ca_approved_date_by_mgr = models.DateTimeField(null=True, blank=True)
    ra_description = models.CharField(max_length=200,null=True, blank=True)
    ra_action_effective = models.CharField(null=True, blank=True, max_length=1, choices=EFFECTIVE_CHOICE)
    ra_followup_date = models.DateTimeField(null=True, blank=True)
    ra_check_by_staff = models.CharField(max_length=3,null=True, blank=True)
    ra_check_date_by_staff = models.DateTimeField(null=True, blank=True)
    ra_check_by_sh = models.CharField(max_length=3,null=True, blank=True)
    ra_check_date_by_sh = models.DateTimeField(null=True, blank=True)
    se_description = models.CharField(max_length=200,null=True, blank=True)
    se_ro_updated = models.CharField(null=True, blank=True, max_length=1, choices=YN_CHOICE)
    se_check_by_mgr = models.CharField(max_length=3,null=True, blank=True) 
    se_check_date_by_mgr = models.DateTimeField(null=True, blank=True)
    se_check_by_qa = models.CharField(max_length=3,null=True, blank=True)
    se_check_date_by_qa = models.DateTimeField(null=True, blank=True)
    mail_sent_date_1 = models.DateTimeField(null=True, blank=True)
    mail_sent_date_2 = models.DateTimeField(null=True, blank=True)
    mail_sent_date_3 = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=1,null=True, blank=True)
    deadline = models.DateTimeField(null=True, blank=True)
    insert_user_id = models.CharField(max_length=3,null=True, blank=True)
    insert_date = models.DateTimeField(null=True, blank=True)
    update_user_id = models.CharField(max_length=3,null=True, blank=True)
    update_date = models.DateTimeField(null=True, blank=True)
    delete_user_id = models.CharField(max_length=3,null=True, blank=True)
    delete_date = models.DateTimeField(null=True, blank=True)     
    nc_conforme_status = models.CharField(max_length=1, null=True, blank=True)
    ic_approve_status = models.CharField(max_length=1, null=True, blank=True)
    rca_approve_status = models.CharField(max_length=1, null=True, blank=True)
    ca_check_by_sh_status = models.CharField(max_length=1, null=True, blank=True)
    ca_approve_by_mgr_status = models.CharField(max_length=1, null=True, blank=True)
    ra_check_by_staff_status = models.CharField(max_length=1,null=True, blank=True)
    ra_check_by_sh_status = models.CharField(max_length=1, null=True, blank=True)
    se_check_by_mgr_status = models.CharField(max_length=1, null=True, blank=True)
    se_check_by_qa_status = models.CharField(max_length=1, null=True, blank=True)
    close_date = models.DateTimeField(null=True, blank=True)     
    comments = models.TextField(blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'ncr_detail_mstr'        

       
 
class DenyReason(models.Model):
    ncr_no = models.CharField(primary_key=True, max_length=43)
    rev_no = models.IntegerField()
    phase = models.CharField(max_length=1)
    reason = models.CharField(max_length=1000, blank=True, null=True)
    denied_by = models.CharField(max_length=3, blank=True, null=True)
    denied_date = models.DateTimeField(blank=True, null=True)
    accepted_date = models.DateTimeField(blank=True, null=True)
    corrected_by = models.CharField(max_length=3, blank=True, null=True)
    corrected_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'deny_reason'
        unique_together = (('ncr_no', 'rev_no', 'phase'),)



class NcrAdvUserTbl(models.Model):
    chapano = models.CharField(db_column='chapaNo', primary_key=True, max_length=3)
    user_type = models.CharField(db_column='user_type', blank=True, null=True, max_length=1)        
    dept_id = models.TextField(db_column='dept_id', blank=True, null=True, max_length=3)  

    class Meta:
        managed = False
        db_table = 'NCR_ADV_USER_TBL'



class NcrDetailMstrHistory(models.Model):
    ncr_no = models.CharField(max_length=43)
    rev_no = models.IntegerField()
    ncr_issue_date = models.DateTimeField()
    serial_no = models.CharField(max_length=3)
    source = models.CharField(max_length=1, blank=True, null=True)
    other_source = models.CharField(max_length=15, blank=True, null=True)
    classification = models.CharField(max_length=1, blank=True, null=True)
    nc_detail_description = models.CharField(max_length=200, blank=True, null=True)
    nc_discovered_by = models.CharField(max_length=15, blank=True, null=True)
    nc_conformed_by = models.CharField(max_length=3, blank=True, null=True)
    nc_conformed_date = models.DateTimeField(blank=True, null=True)
    ncr_issue_by = models.CharField(max_length=3, blank=True, null=True)
    ic_description = models.CharField(max_length=200, blank=True, null=True)
    ic_incharge = models.CharField(max_length=3, blank=True, null=True)
    ic_create_date = models.DateTimeField(blank=True, null=True)
    ic_approve_by = models.CharField(max_length=3, blank=True, null=True)
    ic_approve_date = models.DateTimeField(blank=True, null=True)
    rca_description = models.CharField(max_length=200, blank=True, null=True)
    ca_necessary = models.CharField(max_length=1, blank=True, null=True)
    rca_incharge = models.CharField(max_length=3, blank=True, null=True)
    rca_create_date = models.DateTimeField(blank=True, null=True)
    rca_approve_by = models.CharField(max_length=3, blank=True, null=True)
    rca_approve_date = models.DateTimeField(blank=True, null=True)
    ca_target_date = models.DateField(blank=True, null=True)
    ca_description = models.CharField(max_length=200, blank=True, null=True)
    ca_create_by = models.CharField(max_length=3, blank=True, null=True)
    ca_create_date = models.DateTimeField(blank=True, null=True)
    ca_checked_by_sh = models.CharField(max_length=3, blank=True, null=True)
    ca_approved_by_mgr = models.CharField(max_length=3, blank=True, null=True)
    ca_check_date_by_sh = models.DateTimeField(blank=True, null=True)
    ca_approved_date_by_mgr = models.DateTimeField(blank=True, null=True)
    ra_description = models.CharField(max_length=200, blank=True, null=True)
    ra_action_effective = models.CharField(max_length=1, blank=True, null=True)
    ra_followup_date = models.DateTimeField(blank=True, null=True)
    ra_check_by_staff = models.CharField(max_length=3, blank=True, null=True)
    ra_check_date_by_staff = models.DateTimeField(blank=True, null=True)
    ra_check_by_sh = models.CharField(max_length=3, blank=True, null=True)
    ra_check_date_by_sh = models.DateTimeField(blank=True, null=True)
    se_description = models.CharField(max_length=200, blank=True, null=True)
    se_ro_updated = models.CharField(max_length=1, blank=True, null=True)
    se_check_by_mgr = models.CharField(max_length=3, blank=True, null=True)
    se_check_date_by_mgr = models.DateTimeField(blank=True, null=True)
    se_check_by_qa = models.CharField(max_length=3, blank=True, null=True)
    se_check_date_by_qa = models.DateTimeField(blank=True, null=True)
    mail_sent_date_1 = models.DateTimeField(blank=True, null=True)
    mail_sent_date_2 = models.DateTimeField(blank=True, null=True)
    mail_sent_date_3 = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    deadline = models.DateTimeField(blank=True, null=True)
    nc_conforme_status = models.CharField(max_length=1, blank=True, null=True)
    ic_approve_status = models.CharField(max_length=1, blank=True, null=True)
    rca_approve_status = models.CharField(max_length=1, blank=True, null=True)
    ca_check_by_sh_status = models.CharField(max_length=1, blank=True, null=True)
    ca_approve_by_mgr_status = models.CharField(max_length=1, blank=True, null=True)
    ra_check_by_sh_status = models.CharField(max_length=1, blank=True, null=True)
    insert_user_id = models.CharField(max_length=3, blank=True, null=True)
    insert_date = models.DateTimeField(blank=True, null=True)
    update_user_id = models.CharField(max_length=3, blank=True, null=True)
    update_date = models.DateTimeField(blank=True, null=True)
    delete_user_id = models.CharField(max_length=3, blank=True, null=True)
    delete_date = models.DateTimeField(blank=True, null=True)
    dept_id = models.CharField(max_length=3)
    project_id = models.CharField(max_length=3)
    se_check_by_mgr_status = models.CharField(max_length=1, blank=True, null=True)
    se_check_by_qa_status = models.CharField(max_length=45, blank=True, null=True)
    close_date = models.DateTimeField(blank=True, null=True)
    ra_check_by_staff_status = models.CharField(max_length=1, blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'ncr_detail_mstr_history'
        unique_together = (('ncr_no', 'rev_no'),)    
        
        
        
        



