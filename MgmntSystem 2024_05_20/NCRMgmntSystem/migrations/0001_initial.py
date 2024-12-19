# Generated by Django 2.2.5 on 2021-05-20 06:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DenyReason',
            fields=[
                ('ncr_no', models.CharField(max_length=40, primary_key=True, serialize=False)),
                ('rev_no', models.IntegerField()),
                ('phase', models.CharField(max_length=1)),
                ('reason', models.CharField(blank=True, max_length=200, null=True)),
                ('denied_by', models.CharField(blank=True, max_length=3, null=True)),
                ('denied_date', models.DateTimeField(blank=True, null=True)),
                ('accepted_date', models.DateTimeField(blank=True, null=True)),
                ('seq', models.IntegerField()),
                ('corrected_by', models.CharField(blank=True, max_length=3, null=True)),
                ('corrected_date', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'deny_reason',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Dept',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(blank=True, null=True)),
                ('groupid', models.CharField(db_column='groupId', max_length=2)),
            ],
            options={
                'db_table': 'dept',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('chapano', models.CharField(db_column='chapaNo', max_length=3, primary_key=True, serialize=False)),
                ('lastname', models.TextField(blank=True, db_column='lastName', null=True)),
                ('firstname', models.TextField(blank=True, db_column='firstName', null=True)),
                ('middlename', models.TextField(blank=True, db_column='middleName', null=True)),
                ('password', models.TextField(blank=True, null=True)),
                ('status', models.CharField(blank=True, max_length=1, null=True)),
                ('email', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'employee',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='NcrDetailMstrHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ncr_no', models.CharField(max_length=40)),
                ('rev_no', models.IntegerField()),
                ('ncr_issue_date', models.DateTimeField()),
                ('serial_no', models.CharField(max_length=3)),
                ('source', models.CharField(blank=True, max_length=1, null=True)),
                ('other_source', models.CharField(blank=True, max_length=15, null=True)),
                ('classification', models.CharField(blank=True, max_length=1, null=True)),
                ('nc_detail_description', models.CharField(blank=True, max_length=200, null=True)),
                ('nc_discovered_by', models.CharField(blank=True, max_length=15, null=True)),
                ('nc_conformed_by', models.CharField(blank=True, max_length=3, null=True)),
                ('nc_conformed_date', models.DateTimeField(blank=True, null=True)),
                ('ncr_issue_by', models.CharField(blank=True, max_length=3, null=True)),
                ('ic_description', models.CharField(blank=True, max_length=200, null=True)),
                ('ic_incharge', models.CharField(blank=True, max_length=3, null=True)),
                ('ic_create_date', models.DateTimeField(blank=True, null=True)),
                ('ic_approve_by', models.CharField(blank=True, max_length=3, null=True)),
                ('ic_approve_date', models.DateTimeField(blank=True, null=True)),
                ('rca_description', models.CharField(blank=True, max_length=200, null=True)),
                ('ca_necessary', models.CharField(blank=True, max_length=1, null=True)),
                ('rca_incharge', models.CharField(blank=True, max_length=3, null=True)),
                ('rca_create_date', models.DateTimeField(blank=True, null=True)),
                ('rca_approve_by', models.CharField(blank=True, max_length=3, null=True)),
                ('rca_approve_date', models.DateTimeField(blank=True, null=True)),
                ('ca_target_date', models.DateField(blank=True, null=True)),
                ('ca_description', models.CharField(blank=True, max_length=200, null=True)),
                ('ca_create_by', models.CharField(blank=True, max_length=3, null=True)),
                ('ca_create_date', models.DateTimeField(blank=True, null=True)),
                ('ca_checked_by_sh', models.CharField(blank=True, max_length=3, null=True)),
                ('ca_approved_by_mgr', models.CharField(blank=True, max_length=3, null=True)),
                ('ca_check_date_by_sh', models.DateTimeField(blank=True, null=True)),
                ('ca_approved_date_by_mgr', models.DateTimeField(blank=True, null=True)),
                ('ra_description', models.CharField(blank=True, max_length=200, null=True)),
                ('ra_action_effective', models.CharField(blank=True, max_length=1, null=True)),
                ('ra_followup_date', models.DateTimeField(blank=True, null=True)),
                ('ra_check_by_staff', models.CharField(blank=True, max_length=3, null=True)),
                ('ra_check_date_by_staff', models.DateTimeField(blank=True, null=True)),
                ('ra_check_by_sh', models.CharField(blank=True, max_length=3, null=True)),
                ('ra_check_date_by_sh', models.DateTimeField(blank=True, null=True)),
                ('se_description', models.CharField(blank=True, max_length=200, null=True)),
                ('se_ro_updated', models.CharField(blank=True, max_length=1, null=True)),
                ('se_check_by_mgr', models.CharField(blank=True, max_length=3, null=True)),
                ('se_check_date_by_mgr', models.DateTimeField(blank=True, null=True)),
                ('se_check_by_qa', models.CharField(blank=True, max_length=3, null=True)),
                ('se_check_date_by_qa', models.DateTimeField(blank=True, null=True)),
                ('mail_sent_date_1', models.DateTimeField(blank=True, null=True)),
                ('mail_sent_date_2', models.DateTimeField(blank=True, null=True)),
                ('mail_sent_date_3', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(blank=True, max_length=1, null=True)),
                ('deadline', models.DateTimeField(blank=True, null=True)),
                ('nc_conforme_status', models.CharField(blank=True, max_length=1, null=True)),
                ('ic_approve_status', models.CharField(blank=True, max_length=1, null=True)),
                ('rca_approve_status', models.CharField(blank=True, max_length=1, null=True)),
                ('ca_check_by_sh_status', models.CharField(blank=True, max_length=1, null=True)),
                ('ca_approve_by_mgr_status', models.CharField(blank=True, max_length=1, null=True)),
                ('ra_check_by_sh_status', models.CharField(blank=True, max_length=1, null=True)),
                ('insert_user_id', models.CharField(blank=True, max_length=3, null=True)),
                ('insert_date', models.DateTimeField(blank=True, null=True)),
                ('update_user_id', models.CharField(blank=True, max_length=3, null=True)),
                ('update_date', models.DateTimeField(blank=True, null=True)),
                ('delete_user_id', models.CharField(blank=True, max_length=3, null=True)),
                ('delete_date', models.DateTimeField(blank=True, null=True)),
                ('dept_id', models.CharField(max_length=3)),
                ('project_id', models.CharField(max_length=3)),
                ('se_check_by_mgr_status', models.CharField(blank=True, max_length=1, null=True)),
                ('se_check_by_qa_status', models.CharField(blank=True, max_length=45, null=True)),
                ('close_date', models.DateTimeField(blank=True, null=True)),
                ('ra_check_by_staff_status', models.CharField(blank=True, max_length=1, null=True)),
            ],
            options={
                'db_table': 'ncr_detail_mstr_history',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='PositionDetail',
            fields=[
                ('id', models.CharField(max_length=3, primary_key=True, serialize=False)),
                ('positioncd', models.CharField(db_column='positionCd', max_length=3)),
                ('positionnm', models.CharField(db_column='positionNm', max_length=50)),
            ],
            options={
                'db_table': 'positiondetail',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Positions',
            fields=[
                ('id', models.CharField(max_length=3, primary_key=True, serialize=False)),
                ('name', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'positions',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Rank',
            fields=[
                ('chapano', models.CharField(db_column='chapaNo', max_length=3, primary_key=True, serialize=False)),
                ('positionid', models.CharField(db_column='positionId', max_length=3)),
                ('deptid', models.TextField(blank=True, db_column='deptId', null=True)),
            ],
            options={
                'db_table': 'rank',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='NcrAdvUserTbl',
            fields=[
                ('chapano', models.CharField(db_column='chapaNo', max_length=3, primary_key=True, serialize=False)),
                ('user_type', models.CharField(blank=True, db_column='user_type', max_length=1, null=True)),
                ('dept_id', models.TextField(blank=True, db_column='dept_id', max_length=3, null=True)),
            ],
            options={
                'db_table': 'NCR_ADV_USER_TBL',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=130)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('job_title', models.CharField(blank=True, max_length=30)),
                ('bio', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10)),
                ('name', models.CharField(blank=True, max_length=15, null=True)),
                ('archive_location', models.CharField(blank=True, max_length=50, null=True)),
                ('dept', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='NCRMgmntSystem.Dept')),
            ],
            options={
                'db_table': 'project',
                'managed': True,
                'unique_together': {('dept', 'code')},
            },
        ),
        migrations.CreateModel(
            name='NcrDetailMstr',
            fields=[
                ('ncr_no', models.CharField(max_length=40, primary_key=True, serialize=False)),
                ('rev_no', models.IntegerField(blank=True, null=True)),
                ('ncr_issue_date', models.DateTimeField()),
                ('serial_no', models.CharField(max_length=3)),
                ('source', models.CharField(blank=True, choices=[('1', 'Job'), ('2', 'Audit Finding'), ('3', 'Customer Feedback'), ('4', 'Management Action'), ('5', 'Others')], max_length=1, null=True)),
                ('other_source', models.CharField(blank=True, max_length=15, null=True)),
                ('classification', models.CharField(blank=True, choices=[('1', 'Minor'), ('2', 'Major')], max_length=1, null=True)),
                ('nc_detail_description', models.CharField(blank=True, max_length=200, null=True)),
                ('nc_discovered_by', models.CharField(blank=True, max_length=15, null=True)),
                ('nc_conformed_by', models.CharField(blank=True, max_length=3, null=True)),
                ('nc_conformed_date', models.DateTimeField(blank=True, null=True)),
                ('ncr_issue_by', models.CharField(blank=True, max_length=3, null=True)),
                ('ic_description', models.CharField(blank=True, max_length=200, null=True)),
                ('ic_incharge', models.CharField(blank=True, max_length=3, null=True)),
                ('ic_create_date', models.DateTimeField(blank=True, null=True)),
                ('ic_approve_by', models.CharField(blank=True, max_length=3, null=True)),
                ('ic_approve_date', models.DateTimeField(blank=True, null=True)),
                ('rca_description', models.CharField(blank=True, max_length=200, null=True)),
                ('ca_necessary', models.CharField(blank=True, choices=[('1', 'Yes'), ('0', 'No')], max_length=1, null=True)),
                ('rca_incharge', models.CharField(blank=True, max_length=3, null=True)),
                ('rca_create_date', models.DateTimeField(blank=True, null=True)),
                ('rca_approve_by', models.CharField(blank=True, max_length=3, null=True)),
                ('rca_approve_date', models.DateTimeField(blank=True, null=True)),
                ('ca_target_date', models.DateField(blank=True, null=True)),
                ('ca_description', models.CharField(blank=True, max_length=200, null=True)),
                ('ca_create_by', models.CharField(blank=True, max_length=3, null=True)),
                ('ca_create_date', models.DateTimeField(blank=True, null=True)),
                ('ca_checked_by_sh', models.CharField(blank=True, max_length=3, null=True)),
                ('ca_check_date_by_sh', models.DateTimeField(blank=True, null=True)),
                ('ca_approved_by_mgr', models.CharField(blank=True, max_length=3, null=True)),
                ('ca_approved_date_by_mgr', models.DateTimeField(blank=True, null=True)),
                ('ra_description', models.CharField(blank=True, max_length=200, null=True)),
                ('ra_action_effective', models.CharField(blank=True, choices=[('1', 'Yes, proceed to F'), ('0', 'No, Return to C'), ('2', 'For folow-up on date')], max_length=1, null=True)),
                ('ra_followup_date', models.DateTimeField(blank=True, null=True)),
                ('ra_check_by_staff', models.CharField(blank=True, max_length=3, null=True)),
                ('ra_check_date_by_staff', models.DateTimeField(blank=True, null=True)),
                ('ra_check_by_sh', models.CharField(blank=True, max_length=3, null=True)),
                ('ra_check_date_by_sh', models.DateTimeField(blank=True, null=True)),
                ('se_description', models.CharField(blank=True, max_length=200, null=True)),
                ('se_ro_updated', models.CharField(blank=True, choices=[('1', 'Yes'), ('0', 'No')], max_length=1, null=True)),
                ('se_check_by_mgr', models.CharField(blank=True, max_length=3, null=True)),
                ('se_check_date_by_mgr', models.DateTimeField(blank=True, null=True)),
                ('se_check_by_qa', models.CharField(blank=True, max_length=3, null=True)),
                ('se_check_date_by_qa', models.DateTimeField(blank=True, null=True)),
                ('mail_sent_date_1', models.DateTimeField(blank=True, null=True)),
                ('mail_sent_date_2', models.DateTimeField(blank=True, null=True)),
                ('mail_sent_date_3', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(blank=True, max_length=1, null=True)),
                ('deadline', models.DateTimeField(blank=True, null=True)),
                ('insert_user_id', models.CharField(blank=True, max_length=3, null=True)),
                ('insert_date', models.DateTimeField(blank=True, null=True)),
                ('update_user_id', models.CharField(blank=True, max_length=3, null=True)),
                ('update_date', models.DateTimeField(blank=True, null=True)),
                ('delete_user_id', models.CharField(blank=True, max_length=3, null=True)),
                ('delete_date', models.DateTimeField(blank=True, null=True)),
                ('nc_conforme_status', models.CharField(blank=True, max_length=1, null=True)),
                ('ic_approve_status', models.CharField(blank=True, max_length=1, null=True)),
                ('rca_approve_status', models.CharField(blank=True, max_length=1, null=True)),
                ('ca_check_by_sh_status', models.CharField(blank=True, max_length=1, null=True)),
                ('ca_approve_by_mgr_status', models.CharField(blank=True, max_length=1, null=True)),
                ('ra_check_by_staff_status', models.CharField(blank=True, max_length=1, null=True)),
                ('ra_check_by_sh_status', models.CharField(blank=True, max_length=1, null=True)),
                ('se_check_by_mgr_status', models.CharField(blank=True, max_length=1, null=True)),
                ('se_check_by_qa_status', models.CharField(blank=True, max_length=1, null=True)),
                ('close_date', models.DateTimeField(blank=True, null=True)),
                ('dept', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='NCRMgmntSystem.Dept')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='NCRMgmntSystem.Project')),
            ],
            options={
                'db_table': 'ncr_detail_mstr',
                'managed': True,
            },
        ),
    ]