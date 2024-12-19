from django.shortcuts import render
from .models import Employee, Rank, Dept
from .models import NcrDetailMstr, NcrAdvUserTbl, Project, DenyReason
from django.db import connection
from collections import namedtuple
from datetime import date
from .forms import LoginForm, NCRCreateForm, NCRVerifyForm, NCRSearchForm, ProjectForm, ProjectUForm, EmployeePasswordForm
from django.http import Http404
from django.core.mail import send_mail
from django.shortcuts import redirect
import datetime
from django.db import DatabaseError, IntegrityError, OperationalError
from smtplib import SMTPException
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import timedelta
import calendar
from django.http import JsonResponse
from django.utils import timezone

#Maximum number of rows to be displayed per page
MAX_ROWS_PER_PAGE = 10

#For Local Test Server (Development)
#PROJ_URL = 'http://127.0.0.1:8000/ncr/'
PROJ_URL = 'http://localhost:8080/ncr/'

#For Integration Test Server (Development)
#PROJ_URL = 'http://ncr.sdmi.shi.co.jp:82/ncr/'

#For Real Server (Deployment)
#PROJ_URL = 'http://mgmntsystem.sdmi.shi.co.jp/ncr/'

#NCOA04_01
#Logic for displaying log-in page

def login_view(request):
    print('START: login_view')



    form = LoginForm()
    #form = LoginForm(initial={'chapano': '?', 'password': ''})   
    context = {'form': form}    

    print('END: login_view')
    return render(request, 'NCRMgmntSystem/login.html', context)  
#NCOA04_02
#Save variables in session then displays the 'Create NCR' page if inputs are valid otherwise display error messages on log-in page
def login(request):
    print('START: login')




    form = None
    e = None
    dept_id = ''
    error_message = ''
    isChecker = False
    isSH = False
    isGrpMgr = False
    isQA = False
    isAdmin = False

    if request.method != 'POST':
        raise Http404('Only POSTs are allowed')
    else:
        form = LoginForm(request.POST or None)   

    if form.is_valid(): # All validation rules pass        
        chapano = form.cleaned_data.get('chapano', None)
        password = form.cleaned_data.get('password', None)

        try:
            e = Employee.objects.get(chapano=chapano)

            if e.password == password:    
                if NcrAdvUserTbl.objects.filter(chapano=chapano, user_type='1').count() > 0:
                    isChecker = True

                if NcrAdvUserTbl.objects.filter(chapano=chapano, user_type='2').count() > 0:
                    isSH = True

                if NcrAdvUserTbl.objects.filter(chapano=chapano, user_type='3').count() > 0:
                    isGrpMgr = True

                if NcrAdvUserTbl.objects.filter(chapano=chapano, user_type='4').count() > 0:
                    isQA = True    

                if NcrAdvUserTbl.objects.filter(chapano=chapano, user_type='5').count() > 0:
                    isAdmin = True

                dept_id = ''            
                try:
                    r = Rank.objects.get(chapano=chapano)  
                    dept_id = r.deptid
                except Rank.DoesNotExist:
                    pass  

                # Clear an item from the session:
                if "logged_user_chapa_no" in request.session:    
                    del request.session["logged_user_chapa_no"]
                if "logged_username" in request.session:    
                    del request.session["logged_username"]  
                if "logged_user_dept_id" in request.session:    
                    del request.session["logged_user_dept_id"]   
                if "isChecker" in request.session:    
                    del request.session["isChecker"]   
                if "isSH" in request.session:    
                    del request.session["isSH"]  
                if "isGrpMgr" in request.session:    
                    del request.session["isGrpMgr"]      
                if "isQA" in request.session:    
                    del request.session["isQA"]       
                if "isAdmin" in request.session:    
                    del request.session["isAdmin"]          
                # Set a session value:
                request.session["logged_user_chapa_no"] = e.chapano 
                request.session["logged_username"] = e.chapano + " - " + e.lastname + ", " + e.firstname + " " + e.middlename 
                request.session["logged_user_dept_id"] = dept_id
                request.session["isChecker"] = isChecker
                request.session["isSH"] = isSH
                request.session["isGrpMgr"] = isGrpMgr
                request.session["isQA"] = isQA
                request.session["isAdmin"] = isAdmin




                if isChecker or isSH or isGrpMgr:    
                    print('END: login')
                    return redirect('/ncr/ncr_verify_list_view')

                else:
                    print('END: login')
                    return redirect('/ncr/ncr_create_view_ins')

            else:    
                error_message = "Your chapaNo and password didn't match."

        except Employee.DoesNotExist:
            error_message = "Your chapaNo is invalid."
    else:  
        form = LoginForm()

    context = {'form': form, 'error_message': error_message, }    

    print('END: login')
    return render(request, 'NCRMgmntSystem/login.html', context)          


def login_via_email(request, mail_user_id):
    print('START: login_via_email')

    e = None

    try:
        e = Employee.objects.get(chapano=mail_user_id)
        isChecker = False
        isSH = False
        isGrpMgr = False
        isQA = False
        isAdmin = False

        if NcrAdvUserTbl.objects.filter(chapano=mail_user_id, user_type='1').count() > 0:
            isChecker = True

        if NcrAdvUserTbl.objects.filter(chapano=mail_user_id, user_type='2').count() > 0:
            isSH = True

        if NcrAdvUserTbl.objects.filter(chapano=mail_user_id, user_type='3').count() > 0:
            isGrpMgr = True

        if NcrAdvUserTbl.objects.filter(chapano=mail_user_id, user_type='4').count() > 0:
            isQA = True

        if NcrAdvUserTbl.objects.filter(chapano=mail_user_id, user_type='5').count() > 0:
            isAdmin = True

        dept_id = ''            
        try:
            r = Rank.objects.get(chapano=mail_user_id)  
            dept_id = r.deptid
        except Rank.DoesNotExist:
            pass

        # Clear an item from the session:
        if "logged_user_chapa_no" in request.session:    
            del request.session["logged_user_chapa_no"]
        if "logged_username" in request.session:    
            del request.session["logged_username"]  
        if "logged_user_dept_id" in request.session:    
            del request.session["logged_user_dept_id"]      
        if "isChecker" in request.session:    
            del request.session["isChecker"]   
        if "isSH" in request.session:    
            del request.session["isSH"]  
        if "isGrpMgr" in request.session:    
            del request.session["isGrpMgr"]   
        if "isQA" in request.session:    
            del request.session["isQA"]       
        if "isAdmin" in request.session:    
            del request.session["isAdmin"]          

        # Set a session value:
        request.session["logged_user_chapa_no"] = e.chapano 
        request.session["logged_username"] = e.chapano + " - " + e.lastname + ", " + e.firstname + " " + e.middlename
        request.session["logged_user_dept_id"] = dept_id
        request.session["isChecker"] = isChecker
        request.session["isSH"] = isSH
        request.session["isGrpMgr"] = isGrpMgr
        request.session["isQA"] = isQA
        request.session["isAdmin"] = isAdmin



    except Employee.DoesNotExist:
        pass

    print('END: login_via_email')
    return
#NCOA04_03
#Delete variables save in session then redisplay log-in page
def logout(request):
    print('START: logout')
    
    # Clear an item from the session:
    if "logged_user_chapa_no" in request.session:    
        del request.session["logged_user_chapa_no"]
    if "logged_username" in request.session:    
        del request.session["logged_username"]   
    if "logged_user_dept_id" in request.session:    
        del request.session["logged_user_dept_id"]         
    if "isChecker" in request.session:    
        del request.session["isChecker"]   
    if "isSH" in request.session:    
        del request.session["isSH"]  
    if "isGrpMgr" in request.session:    
        del request.session["isGrpMgr"]   
    if "isQA" in request.session:    
        del request.session["isQA"]    
    if "isAdmin" in request.session:    
        del request.session["isAdmin"]          
    
    #form = LoginForm() 
    
    
    #NOT NECESSARY 2024/04/16
    if "isChecked" in request.session:
        del request.session["isChecked"]

    #Start modifying due to bug Edric 2024/03/11
    """
    #form = LoginForm(initial={'chapano': '', 'password': ''})   
    
    #context = {'form': form}  
    
    
    #return render(request, 'NCRMgmntSystem/login.html', context)  """
    print('END: login')
    return redirect('/ncr/')
#End modifying due to bug Edric 2024/03/11

def project_add(request): 
    print('START: project_add')
    
    success_message = ''
    error_message = ''
    dept_name = ''
    
    if "logged_user_chapa_no" in request.session:
        logged_user_chapa_no = request.session["logged_user_chapa_no"] 
        
        if "logged_username" in request.session:
            logged_username = request.session["logged_username"]         
            
        if "logged_user_dept_id" in request.session:    
            logged_user_dept_id = request.session["logged_user_dept_id"]      
            
        if "isChecker" in request.session:    
            isChecker = request.session["isChecker"] 
            
        if "isSH" in request.session:    
            isSH = request.session["isSH"]
            
        if "isGrpMgr" in request.session:    
            isGrpMgr = request.session["isGrpMgr"]
            
        if "isAdmin" in request.session:    
            isAdmin = request.session["isAdmin"]  
    
        if request.method == "POST":  
            form = ProjectForm(request.POST)  
            p = Project()
            

        
            if form.is_valid():  
                code = form.cleaned_data['code']  
                name = form.cleaned_data['name']  
                archive_location = form.cleaned_data['archive_location']  
                dept = form.cleaned_data['dept']  
                
                
                
                #if Project.objects.filter(name=name).count() > 0:
                #    error_message = 'Error record with same NAME already exist.'
                #elif Project.objects.filter(code=code).count() > 0:
                #    error_message = 'Error record with same CODE already exist.'
                



                """
                
                #Start modifying Edric 2024/04/24
                if Project.objects.filter(code=code).filter(dept=dept).count() > 0:
                    error_message = 'Error record with same CODE AND SECTION already exist.'    
                else:
                    try:                
                        p.code = code
                        p.name = name
                        p.archive_location = archive_location
                        p.dept = dept
                        p.insert_user_id = logged_user_chapa_no
                        p.save()  
                        success_message = 'Data successfully added in database.'
                
                """



                if code in ('',None) or name in('',None):
                    error_message = "<p>There Were some errors in the information you entered. Please correct the following:</p><ul>"
                    if  code in ('', None):
                        error_message = error_message + '<li>Code: This field is required.</li>'
                    if name in ('',None):
                        error_message = error_message + '<li>Name: This field is required.</li>'
                    error_message = error_message + "</ul>"
                    
                elif Project.objects.filter(code=code).filter(dept=dept).count() > 0:
                    error_message = 'Error record with same CODE AND SECTION already exist.'    
    
                else:
                    try:
                        
                        if ' ' in code:
                            code = code.replace(' ', '')
                            #error_message = "Spaces on code is removed"
                        p.code = code
                        p.name = name
                        p.archive_location = archive_location
                        p.dept = dept
                        p.insert_user_id = logged_user_chapa_no
                        p.save()  
                        success_message = 'Data successfully added in database.'
                        
                        #End modifying
                            
                    except OperationalError:  
                        error_message = 'Error occured while inserting data in database.'
                        pass
                    except DatabaseError:      
                        error_message = 'Error occured while inserting data in database.'
                        pass       
        else:              
            if isAdmin:
                form = ProjectForm() 
            #elif isSH:
            #    form = ProjectForm(initial={
            #        'dept' : logged_user_dept_id
            #        })
            else:
                form = ProjectForm(initial={
                    'dept' : logged_user_dept_id
                    })

        try:
            d = Dept.objects.get(id=logged_user_dept_id)
            dept_name = d.name
        except Dept.DoesNotExist:
            error_message = 'Record with id = ' + logged_user_dept_id + ' doesn''t exist in Dept table.'

        context = {'form': form, 
                   'success_message' : success_message , 
                   'error_message': error_message,
                   'logged_user_chapa_no' : logged_user_chapa_no,
                   'logged_username': logged_username,
                   'isChecker': isChecker,
                   'isSH': isSH,
                   'isGrpMgr': isGrpMgr,
                   'isAdmin': isAdmin,
                   'dept_name' : dept_name,
                   'dept_id' : logged_user_dept_id
                   }   
        return render(request,'NCRMgmntSystem/project_add.html', context)  

    else:        
        print('END: project_add')
        return redirect('/ncr/logout')    


def project_update_view(request, id): 
    print('START: project_update_view')
    
    success_message = ''
    error_message = ''
    
    if "logged_user_chapa_no" in request.session:
        logged_user_chapa_no = request.session["logged_user_chapa_no"] 

        if "logged_username" in request.session:
            logged_username = request.session["logged_username"]         
            
        if "isChecker" in request.session:    
            isChecker = request.session["isChecker"] 
            
        if "isSH" in request.session:    
            isSH = request.session["isSH"]
            
        if "isGrpMgr" in request.session:    
            isGrpMgr = request.session["isGrpMgr"]
            
        if "isAdmin" in request.session:    
            isAdmin = request.session["isAdmin"]  
    
        try:
            p = Project.objects.get(id=id)  
        except Project.DoesNotExist:
            error_message = "Record with id = " + id + "does not exist in Project table."
            pass        
        
        form = ProjectUForm(initial={
                    'project_id' : p.id,   
                    'dept' : p.dept, 
                    'code' : p.code, 
                    'name' : p.name,                    
                    'archive_location' : p.archive_location,
                    'insert_user_id' : p.insert_user_id
                    })
        
        context = {'form': form, 
                   'success_message' : success_message , 
                   'error_message': error_message,
                   'logged_user_chapa_no' : logged_user_chapa_no,
                   'logged_username': logged_username,
                   'isChecker': isChecker,
                   'isSH': isSH,
                   'isGrpMgr': isGrpMgr,
                   'isAdmin': isAdmin,
                   'data': p
                   }   
        print('END: project_update_view')
        return render(request,'NCRMgmntSystem/project_update.html', context)  

    else:        
        print('END: project_update_view')
        return redirect('/ncr/logout') 

    
def project_update(request, id): 
    print('START: project_update')
    
    success_message = ''
    error_message = ''
    
    if "logged_user_chapa_no" in request.session:
        logged_user_chapa_no = request.session["logged_user_chapa_no"] 
        
        if "logged_username" in request.session:
            logged_username = request.session["logged_username"]         
            
        if "isChecker" in request.session:    
            isChecker = request.session["isChecker"] 
            
        if "isSH" in request.session:    
            isSH = request.session["isSH"]
            
        if "isGrpMgr" in request.session:    
            isGrpMgr = request.session["isGrpMgr"]
            
        if "isAdmin" in request.session:    
            isAdmin = request.session["isAdmin"]  
    
        try:
            p = Project.objects.get(id=id)  
        except Project.DoesNotExist:
            error_message = "Record with id = " + id + "does not exist in Project table."
            pass        
        
        if request.method == "POST":  
            form = ProjectUForm(request.POST)  
            
            if form.is_valid():  
                name = form.cleaned_data['name']  
                archive_location = form.cleaned_data['archive_location']  
            
                if Project.objects.filter(name=name).count() > 0:
                    error_message = 'Error record with same NAME already exist.'
                else:
                    
                    try:  
                        print(">>>TESSSETTTTTTINGG")
                        p = Project.objects.get(id=id)
                        p.name = name
                        p.archive_location = archive_location
                        p.save()  
                        success_message = 'Data successfully updated in database.'
                
                    except:      
                        error_message = 'Error occured while updating data in database.'
                        pass    
                
            context = {'form': form, 
               'success_message' : success_message , 
               'error_message': error_message,
               'logged_user_chapa_no' : logged_user_chapa_no,
               'logged_username': logged_username,
               'isChecker': isChecker,
               'isSH': isSH,
               'isGrpMgr': isGrpMgr,
               'isAdmin': isAdmin,
               'data': p
               }  
            
            print('END: project_update')
            return render(request,'NCRMgmntSystem/project_update.html', context)     

    else:        
        print('END: project_update')
        return redirect('/ncr/logout') 


def projects_show(request):
    print('START: projects_show')
    
    form = None        
    error_message = ''
    page_obj = None
    
    logged_user_chapa_no = ''
    logged_username = ''
    logged_user_dept_id = ''
    isChecker = False
    isSH = False
    isGrpMgr = False
    isAdmin = False
    
    if "logged_user_chapa_no" in request.session:
        logged_user_chapa_no = request.session["logged_user_chapa_no"] 
        
        if "logged_username" in request.session:
            logged_username = request.session["logged_username"]         
            
        if "logged_user_dept_id" in request.session:    
            logged_user_dept_id = request.session["logged_user_dept_id"]      
            
        if "isChecker" in request.session:    
            isChecker = request.session["isChecker"] 
            
        if "isSH" in request.session:    
            isSH = request.session["isSH"]
            
        if "isGrpMgr" in request.session:    
            isGrpMgr = request.session["isGrpMgr"]
            
        if "isAdmin" in request.session:    
            isAdmin = request.session["isAdmin"]    
        
        form = NCRSearchForm(request.POST)
        
        sqlStmt = "SELECT a.*, @rownum:=(@rownum+1) AS row_num FROM ("
        sqlStmt = sqlStmt + """SELECT p.id AS id, d.code as section_code, d.name AS section_name, 
                             p.code AS project_code, p.name AS project_name, 
                             p.archive_location as archive_location, p.insert_user_id AS insert_user_id 
                             FROM project p, dept d WHERE d.id = p.dept_id """
                   
        if not isAdmin:
            sqlStmt = sqlStmt + "AND dept_id = '" + logged_user_dept_id + "' "
                                
        #sqlStmt = sqlStmt + "ORDER BY p.dept_id ASC, p.code ASC" 
        sqlStmt = sqlStmt + "ORDER BY d.code ASC, p.code ASC" 
        sqlStmt = sqlStmt + ") a;"
        
        try:
            cursor=connection.cursor()
            cursor.execute("SET @rownum:=0;")
        except DatabaseError:
            error_message = 'Error'                           
        finally:    
            cursor.close
          
        with connection.cursor() as c:
            c.execute(sqlStmt)
            projects = namedtuplefetchall(c)
            rec_cnt = c.rowcount
            
        paginator = Paginator(projects, MAX_ROWS_PER_PAGE) # Show rows per page.
        
        #page_number = request.GET.get('page')    
        if not request.GET.get('page') in [None, '']:    
            page_number = request.GET.get('page')  
        else:    
            page_number = 1  
        
        try:
            page_obj = paginator.get_page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
            error_message = 'No record found.'
        
        if not request.GET.get('error_message') in [None, '']:    
            error_message = request.GET.get('error_message')    
        
        context = {'form': form,
                   'page_obj': page_obj,
                   'logged_user_chapa_no': logged_user_chapa_no,
                   'rec_cnt' : rec_cnt,
                   'logged_username' : logged_username,
                   'isChecker' : isChecker,
                   'isSH' : isSH,
                   'isGrpMgr' : isGrpMgr,
                   'isAdmin' : isAdmin,
                   'error_message' : error_message,
                   'page' : page_number 
                   }    
        print('END: projects_show')
        return render(request, 'NCRMgmntSystem/project_list_show.html', context)
    
    else:
        print('END: projects_show')
        return redirect('/ncr/logout')
    
#def project_delete(request, id):  
def project_delete(request, id, sectionCode, projectCode, page):      
    print('START: project_delete')
    
    #try:  
    #    p = Project.objects.get(id=id)
    #    p.delete()  
    #except DatabaseError as e:   
    #    error_message = 'Error occured while deleting data in database.'
    #    return render(request, 'NCRMgmntSystem/project_list_show.html', {'error_message' : error_message})
    #    pass    
    if NcrDetailMstr.objects.filter(project_id=id).count() > 0:
        #error_message = 'Cannot delete this project code because a NCR using this code exist.'
        #return render(request, 'NCRMgmntSystem/project_list_show.html', {'error_message' : error_message})
        error_message = 'Cannot delete this record with section code = ' + sectionCode + ' and project code = ' + projectCode +' because a registered NCR is using it.'
        redirectString = '/ncr/projects_show?page=' + str(page) + '&error_message=' + error_message
        return redirect(redirectString)
        pass 
    else:        
        try:  
            
            
            p = Project.objects.get(id=id)
            p.delete()  
        except DatabaseError as e:   
            error_message = 'Error occured while deleting data in database.'
            return render(request, 'NCRMgmntSystem/project_list_show.html', {'error_message' : error_message})
            pass 

    print('END: project_delete')
    return redirect('/ncr/projects_show')


def ncr_search_view_init(request):
    print('START: ncr_search_view_init')
    
    form = None        
    error_message = ''
    page_obj = None
    
    logged_user_chapa_no = ''
    logged_username = ''
    logged_user_dept_id = ''
    isChecker = False
    isSH = False
    isGrpMgr = False
    isQA = False
    isAdmin = False
    
    if "logged_user_chapa_no" in request.session:
        logged_user_chapa_no = request.session["logged_user_chapa_no"] 
        
        ic_incharge_name_initial = ''   
        try:
            e = Employee.objects.get(chapano=logged_user_chapa_no)
            ic_incharge_name_initial = e.lastname + ', ' + e.firstname + ' ' + e.middlename
            
        except Employee.DoesNotExist:
            error_message = "Your chapaNo is invalid." 

        if "logged_username" in request.session:
            logged_username = request.session["logged_username"]   
            
        if "logged_user_dept_id" in request.session:
            logged_user_dept_id = request.session["logged_user_dept_id"]       
            
        if "isChecker" in request.session:    
            isChecker = request.session["isChecker"] 
            
        if "isSH" in request.session:    
            isSH = request.session["isSH"]
            
        if "isGrpMgr" in request.session:    
            isGrpMgr = request.session["isGrpMgr"]
            
        if "isQA" in request.session:    
            isQA = request.session["isQA"]    
            
        if "isAdmin" in request.session:    
            isAdmin = request.session["isAdmin"]    
        #Added WHEN n.status = '7' THEN 'Cancel Request'  Edric Marinas 2024/04/11
        sqlStmt = """SELECT ncr_no, 
                         CASE WHEN n.classification = '1' THEN  'Minor' 
                             WHEN n.classification = '2' THEN  'Major' 
                         End as classification,
                         n.nc_detail_description as nc_detail_description, 
                         d.name as dept_id, 
                         p.name as project_id, 
                         e1.chapaNo as ic_incharge, 
                         CONCAT(e1.lastName, ', ', e1.firstName, ' ', e1.middleName) as ic_incharge_name, 
                         CASE WHEN coalesce(n.nc_detail_description, '') != '' AND coalesce(n.ic_description, '') = '' THEN 'A. Nonconformance detail description' 
                             WHEN coalesce(n.ic_description, '') != '' AND coalesce(n.rca_description, '') = '' THEN 'B. Immediate Correction' 
                             WHEN coalesce(n.rca_description, '') != '' AND coalesce(n.ca_description, '') = '' THEN 'C. Root Cause Analysis' 
                             WHEN coalesce(n.ca_description, '') != ''  AND coalesce(n.ra_description, '') = '' THEN 'D. Corrective Action to the cause' 
                             WHEN coalesce(n.ra_description, '') != '' AND coalesce(n.se_description, '') = '' THEN 'E. Result of action' 
                             WHEN coalesce(n.se_description, '') != '' THEN 'F. Show Effectiveness'           
                         END as progress,
                         n.update_user_id as update_user_id,
                         CASE WHEN n.status = '1' THEN 'Issued' 
                             WHEN n.status = '2' THEN 'Cancelled' 
                             WHEN n.status = '3' THEN 'Accepted' 
                             WHEN n.status = '4' THEN 'On-going' 
                             WHEN n.status = '5' THEN 'Closed' 
                             WHEN n.status = '7' THEN 'Cancel Request' 
                             ELSE '' 
                         End as status,
                         n.ncr_issue_by,
                         n.nc_conforme_status
                     FROM NCR_DETAIL_MSTR n
                         LEFT JOIN DEPT d ON (trim(n.dept_id) =  trim(d.id))
                         LEFT JOIN PROJECT p ON (n.project_id =  p.id AND trim(n.dept_id = p.dept_id))
                         LEFT JOIN EMPLOYEE e1 ON (n.ic_incharge =  e1.chapaNo)                         
                     WHERE n.delete_date IS NULL"""   
        
        if not (isGrpMgr or isQA or isAdmin):             
            if not (isSH or isChecker): 
                sqlStmt = sqlStmt + "    AND e1.chapaNo = '" + logged_user_chapa_no + "'"  
                
            if not logged_user_dept_id in [None, '']:    
                sqlStmt = sqlStmt + " AND TRIM(n.dept_id) = TRIM('" + logged_user_dept_id + "')" 
        
        sqlStmt = sqlStmt + " ORDER BY n.update_date DESC"    
        
        sqlStmtX = "SELECT a.*, @rownum:=(@rownum+1) AS row_num from ("
        sqlStmtX = sqlStmtX + sqlStmt
        sqlStmtX = sqlStmtX + ") a;"
        
        try:
            cursor=connection.cursor()
            cursor.execute("SET @rownum:=0;")
        except DatabaseError:
            error_message = 'Error'                           
        finally:    
            cursor.close

        with connection.cursor() as c:
            c.execute(sqlStmtX)
            ncr_stat_view_list = namedtuplefetchall(c)
            rec_cnt = c.rowcount

        paginator = Paginator(ncr_stat_view_list, MAX_ROWS_PER_PAGE) # Show rows per page.
        page_number = request.GET.get('page')    

        try:
            page_obj = paginator.get_page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
            error_message = 'Sorry! No record found for your query.'
        
        if isGrpMgr or isQA or isAdmin:  
            form = NCRSearchForm()  
        elif isChecker or isSH:  
            form = NCRSearchForm(initial={'dept': logged_user_dept_id,})   
        else:
            form = NCRSearchForm(initial={'ic_incharge': ic_incharge_name_initial, 'dept': logged_user_dept_id,})    

        if not (isGrpMgr or isQA or isAdmin) and not logged_user_dept_id in [None, '']:  
            form.fields['dept'].widget.attrs['disabled'] = True

            #sqlStmt = "SELECT p.id AS id, CONCAT(p.code, '::', p.name) AS project_name FROM project p WHERE p.dept_id = '"  + str(logged_user_dept_id) + "'"
            sqlStmt = "SELECT p.id AS id, CONCAT(p.code, '::', p.name) AS project_name FROM project p WHERE p.dept_id = '"  + str(logged_user_dept_id) + "' ORDER BY p.code"                  

            with connection.cursor() as c:
                c.execute(sqlStmt)
                projects = namedtuplefetchall(c)                     
                projects.insert(0, ['', '---------'])
                form.fields['project'].choices = projects 

        context = {'form': form,
                   'page_obj': page_obj,
                   'logged_user_chapa_no': logged_user_chapa_no,
                   'rec_cnt' : rec_cnt,
                   'logged_username' : logged_username,
                   "isChecker" : isChecker,
                   "isSH" : isSH,
                   "isGrpMgr" : isGrpMgr,
                   "isAdmin" : isAdmin,
                   "isQA" : isQA, 
                   }  

        print('END: ncr_search_view_init')
        return render(request, 'NCRMgmntSystem/ncr_search.html', context)

    else:
        print('END: ncr_search_view_init')
        return redirect('/ncr/logout')


def ncr_search_view(request):
    print('START: ncr_search_view')

    form = None        
    error_message = ''
    page_obj = None

    logged_user_chapa_no = ''
    logged_username = ''
    logged_user_dept_id = ''
    isChecker = False
    isSH = False
    isGrpMgr = False
    isQA = False
    isAdmin = False

    ncr_no = request.POST.get('ncr_no', None)
    ncr_no_like_cond = request.POST.get('ncr_no_like_cond', None)
    progress = request.POST.get('progress', None)
    dept_id = request.POST.get('dept', None)


    search = request.POST.get('search', None)
    print("search >>" + str(search))

    page = request.POST.get('page', None)
    print("page >>" + str(page))

    #selected_dept = request.GET.get('dept') 
    #selected_dept = request.POST.get('selected_dept', None)
    #print("selected_dept >>" + str(selected_dept))

    project_id = request.POST.get('project', None)
    ic_incharge = request.POST.get('ic_incharge', None)
    ic_incharge_like_cond = request.POST.get('ic_incharge_like_cond', None)
    classification_list = request.POST.getlist('classification')
    progress_list = request.POST.getlist('progress')
    status = request.POST.get('status', None)
    deadline = request.POST.getlist('deadline')
    isQA = False
           
    if "logged_user_chapa_no" in request.session:
        logged_user_chapa_no = request.session["logged_user_chapa_no"] 

        if "logged_username" in request.session:
            logged_username = request.session["logged_username"]
            
        if "logged_user_dept_id" in request.session:
            logged_user_dept_id = request.session["logged_user_dept_id"]         
            
        if "isChecker" in request.session:    
            isChecker = request.session["isChecker"] 
            
        if "isSH" in request.session:    
            isSH = request.session["isSH"]
            
        if "isGrpMgr" in request.session:    
            isGrpMgr = request.session["isGrpMgr"]
            
        if "isQA" in request.session:    
            isQA = request.session["isQA"]     
            
        if "isAdmin" in request.session:    
            isAdmin = request.session["isAdmin"]    
        
        if not (isGrpMgr or isQA or isAdmin):             
            if not logged_user_dept_id in [None, '']: 
                dept_id = logged_user_dept_id        
        
        # create a form instance and populate it with data from the request:
        form = NCRSearchForm(request.POST)
        
        #ncrNoVal = form.get("ncr_no");
        #print("form.ncr_no >>" + str(ncrNoVal))
        
        #deptVal = form.get("dept");
        #print("form.dept >>" + str(deptVal))
         
        
        
        # Added for additional request 
        #WHEN n.status = '7' THEN 'Cancel Request'
        
        sqlStmt = """SELECT ncr_no, 
                         CASE WHEN n.classification = '1' THEN  'Minor' 
                             WHEN n.classification = '2' THEN  'Major' 
                         End as classification,
                         n.nc_detail_description as nc_detail_description, 
                         d.name as dept_id, 
                         p.name as project_id, 
                         e1.chapaNo as ic_incharge, 
                         CONCAT(e1.lastName, ', ', e1.firstName, ' ', e1.middleName) as ic_incharge_name, 
                         CASE WHEN coalesce(n.nc_detail_description, '') != '' AND coalesce(n.ic_description, '') = '' THEN 'A. Nonconformance detail description' 
                             WHEN coalesce(n.ic_description, '') != '' AND coalesce(n.rca_description, '') = '' THEN 'B. Immediate Correction' 
                             WHEN coalesce(n.rca_description, '') != '' AND coalesce(n.ca_description, '') = '' THEN 'C. Root Cause Analysis' 
                             WHEN coalesce(n.ca_description, '') != ''  AND coalesce(n.ra_description, '') = '' THEN 'D. Corrective Action to the cause' 
                             WHEN coalesce(n.ra_description, '') != '' AND coalesce(n.se_description, '') = '' THEN 'E. Result of action' 
                             WHEN coalesce(n.se_description, '') != '' THEN 'F. Show Effectiveness'           
                         END as progress,
                         n.update_user_id as update_user_id,
                         CASE WHEN n.status = '1' THEN 'Issued' 
                             WHEN n.status = '2' THEN 'Cancelled' 
                             WHEN n.status = '3' THEN 'Accepted' 
                             WHEN n.status = '4' THEN 'On-going' 
                             WHEN n.status = '5' THEN 'Closed' 
                             WHEN n.status = '7' THEN 'Cancel Request'
                             ELSE '' 
                         End as status,
                         n.ncr_issue_by,
                         n.nc_conforme_status
                     FROM NCR_DETAIL_MSTR n
                         LEFT JOIN DEPT d ON (trim(n.dept_id) =  trim(d.id))
                         LEFT JOIN PROJECT p ON (n.project_id =  p.id AND trim(n.dept_id = p.dept_id))
                         LEFT JOIN EMPLOYEE e1 ON (n.ic_incharge =  e1.chapaNo)                         
                     WHERE n.delete_date IS NULL"""   
                     
        #check if ncr_no is null or blank    
        if not ncr_no in [None, '']:    
            if ncr_no_like_cond == '1':
                sqlStmt = sqlStmt + " AND TRIM(n.ncr_no) LIKE ('" + ncr_no + "%')" 
            elif ncr_no_like_cond == '2':
                sqlStmt = sqlStmt + " AND TRIM(n.ncr_no) LIKE ('%" + ncr_no + "%')" 
            elif ncr_no_like_cond == '3':
                sqlStmt = sqlStmt + " AND TRIM(n.ncr_no) LIKE ('%" + ncr_no + "')"     
            
        #dept_id:
        if not dept_id in [None, '']:        
            sqlStmt = sqlStmt + " AND TRIM(n.dept_id) = TRIM('" + dept_id + "')" 
            
        #if not selected_dept in [None, '']:        
        #    sqlStmt = sqlStmt + " AND TRIM(n.dept_id) = TRIM('" + selected_dept + "')"     
            
            
       
            
                
        #if project_id:
        if not project_id in [None, '']:            
            sqlStmt = sqlStmt + " AND TRIM(d.id) = TRIM(p.dept_id) AND n.project_id = '" + project_id + "'"               

        #ic_incharge:
        if not ic_incharge in [None, '']:            
            if ic_incharge_like_cond == '1':
                sqlStmt = sqlStmt + " AND CONCAT(e1.lastName, ', ', e1.firstName, ' ', e1.middleName)  LIKE ('" + ic_incharge + "%')" 
            elif ic_incharge_like_cond == '2':
                sqlStmt = sqlStmt + " AND CONCAT(e1.lastName, ', ', e1.firstName, ' ', e1.middleName)  LIKE ('%" + ic_incharge + "%')" 
            elif ic_incharge_like_cond == '3':
                sqlStmt = sqlStmt + " AND CONCAT(e1.lastName, ', ', e1.firstName, ' ', e1.middleName)  LIKE ('%" + ic_incharge + "')" 
        
        #if not status in [None, '']:            
        #    sqlStmt = sqlStmt + " AND n.status = '" + status + "'" 
        if not status in [None, '']:
            if status == '6':
                sqlStmt = sqlStmt + " AND ((n.close_date is null and DATE_FORMAT(sysdate(), '%Y%m%d') > DATE_FORMAT(n.deadline, '%Y%m%d')) or (n.close_date is not null and DATE_FORMAT(n.close_date, '%Y%m%d') > DATE_FORMAT(n.deadline, '%Y%m%d')))"
            else:    
                sqlStmt = sqlStmt + " AND n.status = '" + status + "'" 
        

       
        
       
        

        # Iterate over the classification list
        if len(classification_list) > 0:
            isNext1 = False
            sqlStmt = sqlStmt + " AND n.classification IN ("

            for clssfctn in classification_list:
                if isNext1: 
                    sqlStmt = sqlStmt + ", '" + clssfctn + "'"
                else:    
                    sqlStmt = sqlStmt + "'" + clssfctn + "'"
                    isNext1 = True

            sqlStmt = sqlStmt + ")" 

        # Iterate over the progress_list
        if len(progress_list) > 0:
            isNext2 = False
            sqlStmt = sqlStmt + " AND ("

            for progress in progress_list:
                if isNext2: 
                    sqlStmt = sqlStmt + " OR "
                else:    
                    isNext2 = True           

                if (progress == 'A'):
                    sqlStmt = sqlStmt + " (n.nc_detail_description IS NOT NULL AND n.ic_description IS NULL) "
                elif (progress == 'B'):
                    sqlStmt = sqlStmt + " (n.ic_description IS NOT NULL AND n.rca_description IS NULL)"    
                elif (progress == 'C'):
                    sqlStmt = sqlStmt + " (n.rca_description IS NOT NULL AND n.ca_description IS NULL)"    
                elif (progress == 'D'):
                    sqlStmt = sqlStmt + " (n.ca_description IS NOT NULL AND n.ra_description IS NULL)"    
                elif (progress == 'E'):
                    sqlStmt = sqlStmt + " (n.ra_description IS NOT NULL AND n.se_description IS NULL)"    
                elif (progress == 'F'):
                    sqlStmt = sqlStmt + " n.se_description IS NOT NULL"        
                        
            sqlStmt = sqlStmt + ")"    
                                
        sqlStmt = sqlStmt + " ORDER BY n.ncr_issue_date DESC"    
        
        sqlStmtX = "SELECT a.*, @rownum:=(@rownum+1) AS row_num from ("
        sqlStmtX = sqlStmtX + sqlStmt
        sqlStmtX = sqlStmtX + ") a;"        
                
        try:
            cursor=connection.cursor()
            cursor.execute("SET @rownum:=0;")
        except DatabaseError:
            error_message = 'Error'                           
        finally:    
            cursor.close
                  
        with connection.cursor() as c:
            c.execute(sqlStmtX)
            ncr_stat_view_list = namedtuplefetchall(c)
            rec_cnt = c.rowcount
            
        paginator = Paginator(ncr_stat_view_list, MAX_ROWS_PER_PAGE) # Show rows per page.
        page_number = request.GET.get('page')    
        
        print("page_number >>" + str(page_number))
        
        page_number = page    
        
        print("page_number >>" + str(page_number))
        
            
        try:
            page_obj = paginator.get_page(page_number)
        except PageNotAnInteger:
            if page_number == '<<':
                page_number = 1
            elif page_number == '>>':
                page_number = page_obj.paginator.num_pages
            
            
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
            error_message = 'Sorry! No record found for your query.'
        
        if not (isGrpMgr or isQA or isAdmin) and not logged_user_dept_id in [None, '']:  
            
            #sqlStmt = "SELECT d.id AS id, d.name AS dept_name FROM dept d WHERE d.id = '"  + str(logged_user_dept_id) + "'"
            sqlStmt = "SELECT d.id AS id, d.name AS dept_name FROM dept d WHERE d.id = '"  + str(logged_user_dept_id) + "' ORDER BY d.name"
                 
            with connection.cursor() as c:
                c.execute(sqlStmt)
                depts = namedtuplefetchall(c)                     
                form.fields['dept'].choices = depts    

            form.fields['dept'].widget.attrs['disabled'] = True
            
            #sqlStmt = "SELECT p.id AS id, CONCAT(p.code, '::', p.name) AS project_name FROM project p WHERE p.dept_id = '"  + str(logged_user_dept_id) + "'"
            sqlStmt = "SELECT p.id AS id, CONCAT(p.code, '::', p.name) AS project_name FROM project p WHERE p.dept_id = '"  + str(logged_user_dept_id) + "' ORDER BY p.code"
            
            with connection.cursor() as c:
                c.execute(sqlStmt)
                projects = namedtuplefetchall(c)                     
                projects.insert(0, ['', '---------'])
                form.fields['project'].choices = projects             
        
        context = {'form': form,
                   'page_obj': page_obj,
                   'logged_user_chapa_no': logged_user_chapa_no,
                   'rec_cnt' : rec_cnt,
                   'logged_username' : logged_username,
                   "isChecker" : isChecker,
                   "isSH" : isSH,
                   "isGrpMgr" : isGrpMgr,
                   "isAdmin" : isAdmin,
                   "isQA" : isQA
                   }    
        print('END: ncr_search_view')
        return render(request, 'NCRMgmntSystem/ncr_search.html', context)
    
    else:
        print('END: ncr_search_view')
        return redirect('/ncr/logout')

#NCOA01_01
def ncr_create_view_ins(request):
    print('START : ncr_create_view_ins')






    form = None
    error_message = ''
    template_name  = 'NCRMgmntSystem/ncr_create.html'

    current_date = str(date.today())

    logged_user_chapa_no = ''
    logged_username = ''
    logged_user_dept_id = ''
    isChecker = False 
    isSH = False
    isGrpMgr = False
    isAdmin = False
    
    if "logged_user_chapa_no" in request.session:
        logged_user_chapa_no = request.session["logged_user_chapa_no"] 
        
        if "logged_username" in request.session:
            logged_username = request.session["logged_username"]         
            
        if "logged_user_dept_id" in request.session:    
            logged_user_dept_id = request.session["logged_user_dept_id"]      
            
        if "isChecker" in request.session:    
            isChecker = request.session["isChecker"] 

        if "isSH" in request.session:    
            isSH = request.session["isSH"]

        if "isGrpMgr" in request.session:    
            isGrpMgr = request.session["isGrpMgr"]

        if "isAdmin" in request.session:    
            isAdmin = request.session["isAdmin"]    

        form = NCRCreateForm(initial={'ncr_no': None, 'ncr_issue_date': current_date, 'dept': logged_user_dept_id})

        set_dropdowns(form, logged_user_dept_id)

    else:
       error_message = 'No user is saved in session.'
       template_name = 'NCRMgmntSystem/login.html'

    context = {'form': form, 
               'ncr_no': '', 
               'error_message': error_message, 
               'deny_reasonA' : '', 
               'deny_reasonB' : '', 
               'deny_reasonC' : '', 
               'deny_reasonD' : '', 
               'deny_reasonE' : '', 
               'deny_reasonF' : '',
               'isChecker' : isChecker,
               'isSH' : isSH,
               'isGrpMgr' : isGrpMgr,
               'isAdmin' : isAdmin,
               'logged_username' : logged_username,
               'logged_user_chapa_no' : logged_user_chapa_no}    
    
    print('END : ncr_create_view_ins')
    return render(request, template_name, context) 

#used by reset 
def ncr_create_view(request):
    print('START : ncr_create_view')
    
    ncr_no = request.POST.get("ncr_no")
    
    print('END : ncr_create_view')
    
    if ncr_no in ('', None):
        return redirect('/ncr/ncr_create_view_ins')
    else:    
        return redirect('/ncr/ncr_create_view_upd/' + ncr_no + '/0')    
    
#Used if link from email is clicked        
def ncr_create_view_upd_via_mail(request, ncr_no, user_id):
    print('START : ncr_create_view_upd_via_mail')
    
    login_via_email(request, user_id)
    
    print('END : ncr_create_view_upd_via_mail')
    return redirect('/ncr/ncr_create_view_upd/' + ncr_no + '/0')


def ncr_create_view_upd(request, ncr_no, status):
    print('START : ncr_create_view_upd')
    
    form = None
    message = ''
    template_name = 'NCRMgmntSystem/ncr_create.html'
    n = None
    
    nc_conformed_by_name = ''    
    ic_approve_by_name = ''   
    rca_approve_by_name = ''
    newVal_rca_description = ''
    ca_checked_by_sh_name = '' 
    ra_check_by_sh_name = ''            
    ic_incharge_name = ''
    rca_incharge_name = ''
    ra_check_by_staff_name = ''
    ca_approved_by_mgr_name = ''
    se_check_by_mgr_name = ''
    se_check_by_qa_name = ''
          



    
    deny_reasonA = ''
    deny_reasonB = ''
    deny_reasonC = ''
    deny_reasonD = ''
    deny_reasonE = ''
    deny_reasonF = ''
    
    is_denied_A = '0' 
    is_denied_B = '0' 
    is_denied_C = '0' 
    is_denied_D = '0' 
    is_denied_E = '0' 
    is_denied_F = '0' 
    
    logged_user_chapa_no = ''
    logged_username = ''
    isChecker = False
    isSH = False
    isGrpMgr = False
    isAdmin = False
    
    #Start adding for additional request Edric Marinas 2024/04/04
    a = None
    
    try:
        a =  DenyReason.objects.get(ncr_no=ncr_no,phase='H')

    except:
        error_message = "Error"

    #End adding for additional request Edric Marinas 2024/04/04
    

    
    
    if "logged_user_chapa_no" in request.session:
        
        logged_user_chapa_no = request.session["logged_user_chapa_no"] 
                
        if "logged_username" in request.session:
            logged_username = request.session["logged_username"]         
            
        if "isChecker" in request.session:    
            isChecker = request.session["isChecker"] 
            
        if "isSH" in request.session:    
            isSH = request.session["isSH"]
            
        if "isGrpMgr" in request.session:    
            isGrpMgr = request.session["isGrpMgr"]
            
        if "isAdmin" in request.session:    
            isAdmin = request.session["isAdmin"]    
            

    
            
        try:
            n =  NcrDetailMstr.objects.get(ncr_no=ncr_no)            
            print(n.ncr_no)

            
            #Added Edric Marinas 2024/05/08 
            email = 'None'
            name = n.nc_discovered_by.split(',')
            lastname = name[0]
            
            
            try:
                employee = Employee.objects.filter(lastname=lastname).count()
  
                if employee == 1:
                    employee = Employee.objects.get(lastname=lastname)
                    email = employee.email
                    print(email)
                elif employee > 1:
                    #name = name.split(' ')
                    #firstname = name[1]
                    #employee = Employee.objects.get(lastname=lastname,firstname=firstname)
                    print("has similar lastname")
                else:
                     pass
            except:
                print("No email record")
            #End    
                
                
                
            ncr_issue_date = n.ncr_issue_date
            nc_conformed_date = n.nc_conformed_date
            ic_create_date = n.ic_create_date
            ic_approve_date = n.ic_approve_date
            rca_create_date = n.rca_create_date
            rca_approve_date = n.rca_approve_date
            ca_create_date = n.ca_create_date
            ca_check_date_by_sh = n.ca_check_date_by_sh
            ca_approved_date_by_mgr = n.ca_approved_date_by_mgr 
            ra_check_date_by_staff = n.ra_check_date_by_staff
            ra_check_date_by_sh = n.ra_check_date_by_sh
            se_check_date_by_mgr = n.se_check_date_by_mgr
            se_check_date_by_qa = n.se_check_date_by_qa
                    
            if ncr_issue_date not in [None, '']:
                ncr_issue_date = ncr_issue_date.date
            if nc_conformed_date not in [None, '']:
                nc_conformed_date = nc_conformed_date.date
            if ic_create_date not in [None, '']:
                ic_create_date = ic_create_date.date
            if ic_approve_date not in [None, '']:
                ic_approve_date = ic_approve_date.date      
            if rca_create_date not in [None, '']:
                rca_create_date = rca_create_date.date
            if rca_approve_date not in [None, '']:
                rca_approve_date = rca_approve_date.date    
            if ca_create_date not in [None, '']:
                ca_create_date = ca_create_date.date     
            if ca_check_date_by_sh not in [None, '']:
                ca_check_date_by_sh = ca_check_date_by_sh.date
            if ca_approved_date_by_mgr not in [None, '']:
                ca_approved_date_by_mgr = ca_approved_date_by_mgr.date                 
            if ra_check_date_by_staff not in [None, '']:
                ra_check_date_by_staff = ra_check_date_by_staff.date
            if ra_check_date_by_sh not in [None, '']:
                ra_check_date_by_sh = ra_check_date_by_sh.date
            if se_check_date_by_mgr not in [None, '']:
                se_check_date_by_mgr = se_check_date_by_mgr.date
            if se_check_date_by_qa not in [None, '']:
                se_check_date_by_qa = se_check_date_by_qa.date
            
            if n.nc_conformed_by not in [None, '']:
                try:
                    e = Employee.objects.get(chapano=n.nc_conformed_by)
                    nc_conformed_by_name = e.lastname + ', ' + e.firstname + ' ' + e.middlename
                except Employee.DoesNotExist:
                    nc_conformed_by_name = 'unknown'  
                
            if n.ic_incharge not in [None, '']:
                try:
                    e = Employee.objects.get(chapano=n.ic_incharge)
                    ic_incharge_name = e.lastname + ', ' + e.firstname + ' ' + e.middlename
                except Employee.DoesNotExist:
                    ic_incharge_name = 'unknown'  
                
            if n.ic_approve_by not in [None, '']:
                try:
                    e = Employee.objects.get(chapano=n.ic_approve_by)
                    ic_approve_by_name = e.lastname + ', ' + e.firstname + ' ' + e.middlename
                except Employee.DoesNotExist:
                    ic_approve_by_name = 'unknown'   
                
            if n.rca_incharge not in [None, '']:
                try:
                    e = Employee.objects.get(chapano=n.rca_incharge)
                    rca_incharge_name = e.lastname + ', ' + e.firstname + ' ' + e.middlename
                except Employee.DoesNotExist:
                    rca_incharge_name = 'unknown'                        
                
            if n.rca_approve_by not in [None, '']:
                try:
                    e = Employee.objects.get(chapano=n.rca_approve_by)
                    rca_approve_by_name = e.lastname + ', ' + e.firstname + ' ' + e.middlename
                except Employee.DoesNotExist:
                    rca_approve_by_name = 'unknown'
            
            if n.ca_checked_by_sh not in [None, '']:
                try:
                    e = Employee.objects.get(chapano=n.ca_checked_by_sh)
                    ca_checked_by_sh_name = e.lastname + ', ' + e.firstname + ' ' + e.middlename
                except Employee.DoesNotExist:
                    ca_checked_by_sh_name = 'unknown'      
                
            if n.ca_approved_by_mgr not in [None, '']:
                try:
                    e = Employee.objects.get(chapano=n.ca_approved_by_mgr)
                    ca_approved_by_mgr_name = e.lastname + ', ' + e.firstname + ' ' + e.middlename
                except Employee.DoesNotExist:
                    ca_approved_by_mgr_name = 'unknown'  
                    
            if n.ra_check_by_staff not in [None, '']:
                try:
                    e = Employee.objects.get(chapano=n.ra_check_by_staff)
                    ra_check_by_staff_name = e.lastname + ', ' + e.firstname + ' ' + e.middlename
                except Employee.DoesNotExist:
                    ra_check_by_staff_name = 'unknown'  
                     
            if n.ra_check_by_sh not in [None, '']:
                try:
                    e = Employee.objects.get(chapano=n.ra_check_by_sh)
                    ra_check_by_sh_name = e.lastname + ', ' + e.firstname + ' ' + e.middlename
                except Employee.DoesNotExist:
                    ra_check_by_sh_name = 'unknown' 
            
            if n.se_check_by_mgr not in [None, '']:
                try:
                    e = Employee.objects.get(chapano=n.se_check_by_mgr)
                    se_check_by_mgr_name = e.lastname + ', ' + e.firstname + ' ' + e.middlename
                except Employee.DoesNotExist:
                    se_check_by_mgr_name = 'unknown'
            
            if n.se_check_by_qa not in [None, '']:
                try:
                    e = Employee.objects.get(chapano=n.se_check_by_qa)
                    se_check_by_qa_name = e.lastname + ', ' + e.firstname + ' ' + e.middlename
                except Employee.DoesNotExist:
                    se_check_by_qa_name = 'unknown'

            sqlStmt = """SELECT d.phase as phase, d.reason as reason, DATE_FORMAT(d.denied_date, '%M %d, %Y') as denied_date, 
                concat(e.lastName, ', ' ,  e.firstName, ' ' ,  e.middleName) as denied_by_name
                FROM DENY_REASON d
                LEFT JOIN EMPLOYEE e ON (d.denied_by =  e.chapaNo)
                WHERE d.accepted_date is null """ 
                
            sqlStmt = sqlStmt + " and d.ncr_no = '" + ncr_no + "' and d.rev_no = '" + str(n.rev_no) + "'"   
            
            #for concat value in RCA description 
            if n.ic_approve_date not in [None, ''] and n.ic_approve_status == '1' and n.rca_description in [None, '']:
                 newVal_rca_description = "1. Why " + n.nc_detail_description[0].lower() + n.nc_detail_description[1:] + "?"
            else:
                newVal_rca_description = n.rca_description
            
            with connection.cursor() as c:
                c.execute(sqlStmt)
                deny_reasonB_data = namedtuplefetchall(c)   
                
                for rec in deny_reasonB_data:
                    phase = str(rec[0])
                    reason = str(rec[1])

                    if phase == 'A':
                        deny_reasonA = reason  
                        is_denied_A = 1 

                    elif phase == 'B':
                        deny_reasonB = reason  
                        is_denied_B = 1 
                        
                    elif phase == 'C':
                        deny_reasonC = reason      
                        is_denied_C = '1'             
                        if n.ca_description not in [None, '']:
                            is_denied_D = '1' 
                        
                    elif phase == 'D':
                        deny_reasonD = reason  
                        is_denied_C = '1'             
                        is_denied_D = '1'
                        
                    elif phase == 'E' :
                        deny_reasonE = reason  
                        is_denied_C = '1'             
                        is_denied_D = '1'
                        is_denied_E = '1'
                        
                        if n.se_description not in [None, '']:
                            is_denied_F = '1'
                        
                    elif phase == 'F':
                        deny_reasonF = reason  
                        is_denied_C = '1'             
                        is_denied_D = '1'
                        is_denied_E = '1'
                        is_denied_F = '1'
                        
            ic_approve_by = n.ic_approve_by
            if n.ic_approve_by in [None, ''] and n.nc_conforme_status == '1':
                ic_approve_by = n.nc_conformed_by    
            
            rca_incharge = n.rca_incharge
            if n.rca_incharge in [None, ''] and n.ic_approve_status == '1':
                rca_incharge = n.ic_incharge
                rca_incharge_name = ic_incharge_name
                
            rca_approve_by = n.rca_approve_by
            if n.rca_approve_by in [None, ''] and n.ic_approve_status == '1':
                rca_approve_by = n.ic_approve_by
                
            ca_checked_by_sh = n.ca_checked_by_sh
            if n.ca_checked_by_sh in [None, ''] and n.ic_approve_status == '1':    
                ca_checked_by_sh = n.rca_approve_by    

            ra_check_by_staff = n.ra_check_by_staff
            if n.ra_check_by_staff in [None, ''] and n.ca_approve_by_mgr_status == '1':
                ra_check_by_staff = n.rca_incharge
                ra_check_by_staff_name = rca_incharge_name
                
                
            ra_check_by_sh = n.ra_check_by_sh
            if n.ra_check_by_sh in [None, ''] and n.ca_approve_by_mgr_status == '1':
                ra_check_by_sh = n.rca_approve_by 
                
            se_check_by_mgr = n.se_check_by_mgr
            if n.se_check_by_mgr in [None, ''] and n.ca_approve_by_mgr_status == '1':
                se_check_by_mgr = n.ca_approved_by_mgr    
            
            
            #2024/05/08
            array = n.nc_discovered_by.split("||")
            nc_discoverer_email = ''
            nc_discovered_by = array[0]
            try:
                nc_discoverer_email = array[1]
            except:
                pass

            #initialize form 
            form = NCRCreateForm(initial={                
                    'ncr_no' : n.ncr_no, 
                    'ncr_issue_date' : ncr_issue_date, 
                    'dept' : n.dept, 
                    'project' : n.project.id, 
                    'source' : n.source, 
                    'other_source' : n.other_source, 
                    'classification' : n.classification,                 
                    'nc_detail_description' : n.nc_detail_description,
                    
                    #Start 2024/05/09
                    'nc_discovered_by' : nc_discovered_by,
                    'nc_discoverer_email': nc_discoverer_email,
                    
                    
                    'nc_conformed_by' : n.nc_conformed_by, 
                    'nc_conformed_date' : nc_conformed_date,
                    'ic_description' : n.ic_description, 
                    'ic_incharge' : n.ic_incharge, 
                    'ic_create_date' : ic_create_date, 
                    'ic_approve_by' : ic_approve_by,
                    'ic_approve_date' : ic_approve_date, 
                    'rca_description' : newVal_rca_description,
                    'ca_necessary' : n.ca_necessary, 
                    'rca_incharge' : rca_incharge, 
                    'rca_create_date' : rca_create_date, 
                    'rca_approve_by' : rca_approve_by, 
                    'rca_approve_date' : rca_approve_date, 
                    'ca_target_date' : n.ca_target_date, 
                    'ca_description' : n.ca_description, 
                    'ca_create_by' : n.ca_create_by, 
                    'ca_create_date' : ca_create_date, 
                    'ca_checked_by_sh' : ca_checked_by_sh, 
                    'ca_check_date_by_sh' : ca_check_date_by_sh, 
                    'ca_approved_by_mgr' : n.ca_approved_by_mgr, 
                    'ca_approved_date_by_mgr' : ca_approved_date_by_mgr, 
                    'ra_description' : n.ra_description, 
                    'ra_action_effective' : n.ra_action_effective, 
                    'ra_followup_date' : n.ra_followup_date,
                    'ra_check_by_staff' : ra_check_by_staff,  
                    'ra_check_date_by_staff' : ra_check_date_by_staff, 
                    'ra_check_by_sh' : ra_check_by_sh, 
                    'ra_check_date_by_sh' : ra_check_date_by_sh, 
                    'se_description' : n.se_description, 
                    'se_ro_updated' : n.se_ro_updated,  
                    'se_check_by_mgr' : se_check_by_mgr, 
                    'se_check_date_by_mgr' : se_check_date_by_mgr, 
                    'se_check_by_qa' : n.se_check_by_qa, 
                    'se_check_date_by_qa' : se_check_date_by_qa,
                    'hidden_dept_id' : n.dept.id, 
                    'hidden_mail_sent_date_1' : n.mail_sent_date_1,  
                    'hidden_mail_sent_date_2' : n.mail_sent_date_2,
                    'hidden_mail_sent_date_3' : n.mail_sent_date_3,
                    'hidden_update_date' : n.update_date,
                    'nc_conforme_status' : n.nc_conforme_status,
                    'ic_approve_status' : n.ic_approve_status,
                    'rca_approve_status' : n.rca_approve_status,
                    'ca_check_by_sh_status' : n.ca_check_by_sh_status,
                    'ca_approve_by_mgr_status' : n.ca_approve_by_mgr_status,
                    'ra_check_by_staff_status' : n.ra_check_by_staff_status,
                    'ra_check_by_sh_status' : n.ra_check_by_sh_status,
                    'se_check_by_mgr_status' : n.se_check_by_mgr_status,
                    'se_check_by_qa_status' : n.se_check_by_qa_status,
                    'rev_no' : n.rev_no,                    
                    'is_denied_A' : is_denied_A,
                    'is_denied_B' : is_denied_B,
                    'is_denied_C' : is_denied_C,
                    'is_denied_D' : is_denied_D,
                    'is_denied_E' : is_denied_E,
                    'is_denied_F' : is_denied_F,
                    'status' : n.status,
                    'comments' : n.comments,
                    'is_A_on_edit_mode' : 'X',
                    'is_B_on_edit_mode' : 'X',
                    'is_C_on_edit_mode' : 'X',
                    'is_D_on_edit_mode' : 'X',
                    'is_E_on_edit_mode' : 'X',
                    'is_F_on_edit_mode' : 'X',
                    'ra_check_by_staff_name' : ra_check_by_staff_name,
                    
                    
                    
                    })                     
            set_dropdowns(form, n.dept.id)
            
        except NcrDetailMstr.DoesNotExist:
            message = 'Record with ncr_no = ' + ncr_no + ' doesn''t exist in NcrDetailMstr table.'
    
    else:
        form = LoginForm()         
        context = {'form': form}  
        print('END: ncr_create_view_upd')
        return render(request, 'NCRMgmntSystem/login.html', context)  
    
    if status == 'I':
        message = 'NCR data was succesfully inserted in database.'
    elif status == 'U':
        message = 'NCR data was succesfully updated in database.'
    if status == 'IE':
        try:
            message = request.session["Message"]
            del request.session["Message"]
        except:
            print("No message needed")
            
            #message = 'NCR data was succesfully inserted in database and email notification was sent.'
            
    elif status == 'UE':
        try:
            message = request.session["Message"]
            del request.session["Message"]
        except:
            print("No message needed")
            #message = 'NCR data was succesfully updated in database and email notification was sent.'
            
    
    ncr_no_size = 'S'
    if len(ncr_no) > 25:     
        ncr_no_size = 'L'
    
    context = {
            
               #2024/05/08
               'nc_discoverer_email': nc_discoverer_email,
               'nc_discovered_by' : nc_discovered_by,
        
               #'data2':NcrDetailMstrHistory,
               'form': form, 
               'ncr_no': ncr_no, 
               'message': message, 
               'data' : n, 
               'nc_conformed_by_name' : nc_conformed_by_name,   
               'ic_approve_by_name' : ic_approve_by_name,   
               'rca_approve_by_name' : rca_approve_by_name,
               'ca_checked_by_sh_name' :ca_checked_by_sh_name,
               'ra_check_by_sh_name' : ra_check_by_sh_name,
               'ic_incharge_name' : ic_incharge_name,
               'rca_incharge_name' : rca_incharge_name, 
               'ra_check_by_staff_name' : ra_check_by_staff_name, 
               'ca_approved_by_mgr_name' : ca_approved_by_mgr_name,
               'se_check_by_mgr_name' : se_check_by_mgr_name,
               'se_check_by_qa_name' : se_check_by_qa_name,
               'deny_reasonA' : deny_reasonA, 
               'deny_reasonB' : deny_reasonB, 
               'deny_reasonC' : deny_reasonC, 
               'deny_reasonD' : deny_reasonD, 
               'deny_reasonE' : deny_reasonE, 
               'deny_reasonF' : deny_reasonF,
               'is_denied_A' : is_denied_A,
               'is_denied_B' : is_denied_B,
               'is_denied_C' : is_denied_C,
               'is_denied_D' : is_denied_D,
               'is_denied_E' : is_denied_E,
               'is_denied_F' : is_denied_F,
               "isChecker" : isChecker,
               "isSH" : isSH,
               "isGrpMgr" : isGrpMgr,
               "isAdmin" : isAdmin,
               
               #Start adding for additional request Edric 2024/03/14
               'hidden_update_user_id1' : n.update_user_id,

               "a" : a,
               #End adding for additional request Edric 2024/04/04
               
               
               'logged_username' : logged_username,
               'ncr_no_size' : ncr_no_size,
               'logged_user_chapa_no' : logged_user_chapa_no,
               }    
    
    print('END : ncr_create_view_upd')
    return render(request, template_name, context) 


def ncr_verify_list_view(request):
    print('START: ncr_verify_list_view')
            
    error_message = ''
    page_obj = None
    form = None
    
    if "logged_user_chapa_no" in request.session:
        logged_user_chapa_no = request.session["logged_user_chapa_no"] 
        
        if "logged_username" in request.session:
            logged_username = request.session["logged_username"]         
            
        if "isChecker" in request.session:
            isChecker = request.session["isChecker"]

        if "isSH" in request.session:
            isSH = request.session["isSH"]

        if "isGrpMgr" in request.session:
            isGrpMgr = request.session["isGrpMgr"]

        if "isAdmin" in request.session:    
            isAdmin = request.session["isAdmin"]   

    #Start adding Edric Marinas 2024/03/11
    else:
        error_message = 'No user is saved in session.'
 
        context = {'error_message': error_message}
        return render(request, 'NCRMgmntSystem/login.html', context)
    #end adding Edric Marinas 2024/03/11








    #START MODIFYING FOR IMPROVEMENT Edric 2024/04/23
    #sqlStmt = "SELECT a.*, @rownum:=(@rownum+1) AS row_num from ("
    #sqlStmt = sqlStmt + "SELECT n.ncr_no as ncr_no, n.nc_detail_description, n.deadline, CONCAT(e.lastName, ', ', e.firstName, ' ', e.middleName) as last_update_by_name, n.update_date "
    #sqlStmt = sqlStmt + "FROM ncr_detail_mstr n LEFT JOIN EMPLOYEE e ON (n.update_user_id =  e.chapaNo) "
    #sqlStmt = sqlStmt + "WHERE n.delete_date IS NULL AND n.se_check_date_by_qa IS NULL AND ("
    #sqlStmt = sqlStmt + "(n.nc_conformed_by = '" + logged_user_chapa_no + "' and n.nc_conformed_date IS NULL ) OR "
    #sqlStmt = sqlStmt + "(n.ic_approve_by = '" + logged_user_chapa_no + "' AND n.ic_approve_date IS NULL ) OR "
    #sqlStmt = sqlStmt + "(n.rca_approve_by = '" + logged_user_chapa_no + "' and n.rca_approve_date IS NULL ) OR "
    #sqlStmt = sqlStmt + "(n.ca_checked_by_sh = '" + logged_user_chapa_no + "' and n.ca_check_date_by_sh IS NULL ) OR "
    #sqlStmt = sqlStmt + "(n.ca_approved_by_mgr = '" + logged_user_chapa_no + "' and n.ca_approved_date_by_mgr IS NULL ) OR "
    #sqlStmt = sqlStmt + "(n.ra_check_by_sh = '" + logged_user_chapa_no + "' and n.ra_check_date_by_sh IS NULL ) OR "                 
    #sqlStmt = sqlStmt + "(n.se_check_by_mgr = '" + logged_user_chapa_no + "' and n.se_check_date_by_mgr IS NULL ) OR "
    #sqlStmt = sqlStmt + "(n.se_check_by_qa = '" + logged_user_chapa_no + "' and n.se_check_date_by_qa IS NULL ) )"
    
  
    #Set SQL statement
    sqlStmt = "SELECT a.*, @rownum:=(@rownum+1) AS row_num from ("
    sqlStmt = sqlStmt + "SELECT n.ncr_no as ncr_no, n.nc_detail_description, n.deadline, CONCAT(e.lastName, ', ', e.firstName, ' ', e.middleName) as last_update_by_name, n.update_date "
    sqlStmt = sqlStmt + "FROM ncr_detail_mstr n LEFT JOIN EMPLOYEE e ON (n.update_user_id =  e.chapaNo) "
    sqlStmt = sqlStmt + "WHERE n.delete_date IS NULL AND n.se_check_date_by_qa IS NULL AND ("
    sqlStmt = sqlStmt + "(n.nc_conformed_by = '" + logged_user_chapa_no + "' and (n.nc_conformed_date IS NULL OR n.status = '7') ) OR "
    sqlStmt = sqlStmt + "(n.ic_approve_by = '" + logged_user_chapa_no + "' and (n.ic_approve_date IS NULL OR n.status = '7') ) OR "
    sqlStmt = sqlStmt + "(n.rca_approve_by = '" + logged_user_chapa_no + "' and (n.rca_approve_date IS NULL OR n.status = '7') ) OR "
    sqlStmt = sqlStmt + "(n.ca_checked_by_sh = '" + logged_user_chapa_no + "' and (n.ca_check_date_by_sh IS NULL OR n.status = '7') ) OR "           
    sqlStmt = sqlStmt + "(n.ca_approved_by_mgr = '" + logged_user_chapa_no + "' and (n.ca_approved_date_by_mgr IS NULL OR n.status = '7') ) OR "
    sqlStmt = sqlStmt + "(n.ra_check_by_sh = '" + logged_user_chapa_no + "' and (n.ra_check_date_by_sh IS NULL OR n.status = '7') ) OR "                 
    sqlStmt = sqlStmt + "(n.se_check_by_mgr = '" + logged_user_chapa_no + "' and (n.se_check_date_by_mgr IS NULL OR n.status = '7') ) OR "
    sqlStmt = sqlStmt + "(n.se_check_by_qa = '" + logged_user_chapa_no + "' and (n.se_check_date_by_qa IS NULL OR n.status = '7') ) )"
    sqlStmt = sqlStmt + "AND n.status not in ('5','2')"
    #END MODIFYING FOR IMPROVEMENT Edric 2024/04/26

    #sqlStmt = sqlStmt + " ORDER BY n.ncr_issue_date DESC"   
    sqlStmt = sqlStmt + " ORDER BY n.update_date DESC"   
    sqlStmt = sqlStmt + ") a;"    

    try:
        cursor=connection.cursor()
        cursor.execute("SET @rownum:=0;")
    except DatabaseError as e:
        error_message = 'Error'                           
    finally:    
        cursor.close

    with connection.cursor() as c:
        c.execute(sqlStmt)
        ncr_verify_list = namedtuplefetchall(c)
        rec_cnt = c.rowcount

        paginator = Paginator(ncr_verify_list, MAX_ROWS_PER_PAGE) # Show rows per page.
        page_number = request.GET.get('page')    
    
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
        error_message = 'No record found.'
                
    context = {
        "form": form,
        "page_obj": page_obj,
        "rec_cnt" : rec_cnt,
        "logged_user_chapa_no" : logged_user_chapa_no,
        "logged_username" : logged_username,
        "isChecker" : isChecker,
        "isSH" : isSH,
        "isGrpMgr" : isGrpMgr,
        "isAdmin" : isAdmin,
    }

    print('END: ncr_verify_list_view')
    return render(request, 'NCRMgmntSystem/ncr_verify_list.html', context)


def is_error_on_required(request, form):
    print('START: is_error_on_required')
     
    ca_necessary = form.data.get('ca_necessary')
    
    print('ca_necessary >>' + str(ca_necessary))
    
    ca_description = form.data.get('ca_description')
    ca_target_date = form.data.get('ca_target_date')
    ca_checked_by_sh = form.data.get('ca_checked_by_sh')
    ca_approved_by_mgr = form.data.get('ca_approved_by_mgr')
    reason_action_not_effective = form.data.get('reason_action_not_effective')
    se_description = form.data.get('se_description')
    se_ro_updated = form.data.get('se_ro_updated')
    
    
    hidden_request_cancel = form.data.get('hidden_request_cancel')
    
    print(se_ro_updated)

    ncr_no = form.data.get('ncr_no') 
    
    d_has_input = False    
    f_has_input = False  
    
    has_error = False
    has_errorA = False
    has_errorB = False
    has_errorC = False
    has_errorD = False
    has_errorE = False
    has_errorF = False
    
    

    
    #D. Corrective Action to the cause
    if ca_description not in [None, ''] or ca_target_date not in [None, ''] or ca_checked_by_sh not in [None, ''] or ca_approved_by_mgr not in [None, '']:    
        d_has_input = True
         
    #F. Show Effectiveness  
    if se_description not in [None, ''] or se_ro_updated not in [None, '']: 
        f_has_input = True  
    
    if ncr_no not in ('', None):
        try:
            n =  NcrDetailMstr.objects.get(ncr_no=ncr_no)     
            
            if (str(n.nc_conforme_status) != "1"): 
                has_errorA = is_error_on_required_A(request, form)
    
            elif (str(n.ic_approve_status) != "1"): 
                has_errorB = is_error_on_required_B(request, form)
        
            elif reason_action_not_effective not in ('', None) or str(n.ca_approve_by_mgr_status) != "1": 
                has_errorC = is_error_on_required_C(request, form)
            
                if ca_necessary != '0':
                #    if d_has_input:
                    has_errorD = is_error_on_required_D(request, form)  
                
            elif str(n.se_check_by_qa_status) != "1": 
                has_errorE = is_error_on_required_E(request, form)            
                ra_action_effective = form.data.get('ra_action_effective')
                classification = form.data.get('classification')
                
                if ra_action_effective == '1' and classification == '2':     
                    has_errorF = is_error_on_required_F(request, form)
            
        except NcrDetailMstr.DoesNotExist:
            pass  
    
    else:
        has_errorA = is_error_on_required_A(request, form)

    if hidden_request_cancel == '7':
        has_error = False
    elif has_errorA or has_errorB or has_errorC or has_errorD or has_errorE or has_errorF:     
        has_error = True
    
    
    
        
    
    print('END: is_error_on_required')
    return has_error


def is_error_on_not_changed(request, form):
    print('START: is_error_on_not_changed')
    
    was_not_changed = True
    
    ncr_no = form.cleaned_data['ncr_no']        
    source = form.cleaned_data['source']        
    other_source = form.cleaned_data['other_source']        
    classification = form.cleaned_data['classification']        
    nc_detail_description = form.cleaned_data['nc_detail_description']        
    nc_discovered_by = form.cleaned_data['nc_discovered_by']        
    nc_conformed_by = form.cleaned_data['nc_conformed_by']
    ic_description = form.cleaned_data['ic_description']        
    rca_description = form.cleaned_data['rca_description']        
    ca_necessary = form.cleaned_data['ca_necessary']        
    ca_description = form.cleaned_data['ca_description']        
    ca_target_date = form.cleaned_data['ca_target_date']        
    ca_approved_by_mgr = form.cleaned_data['ca_approved_by_mgr']        
    ra_description = form.cleaned_data['ra_description']        
    ra_action_effective = form.cleaned_data['ra_action_effective']        
    ra_followup_date = form.cleaned_data['ra_followup_date']  
    se_description = form.cleaned_data['se_description']  
    
    se_ro_updated = form.cleaned_data['se_ro_updated']  


    se_check_by_qa = form.cleaned_data['se_check_by_qa']  
    comments = form.cleaned_data['comments']  

    ic_incharge = form.cleaned_data['ic_incharge']        
    ic_approve_by = form.cleaned_data['ic_approve_by']   
    rca_incharge = form.cleaned_data['rca_incharge']        
    rca_approve_by = form.cleaned_data['rca_approve_by']        
    ca_checked_by_sh = form.cleaned_data['ca_checked_by_sh']        
    ra_check_by_staff = form.cleaned_data['ra_check_by_staff']        
    ra_check_by_sh = form.cleaned_data['ra_check_by_sh']        
    se_check_by_mgr = form.cleaned_data['se_check_by_mgr']        

    try:
        n =  NcrDetailMstr.objects.get(ncr_no=ncr_no)     
    except NcrDetailMstr.DoesNotExist:
        pass  

    #A. Nonconformance detail description
    n_source = ''    
    if (n.source not in ('', None)):
        n_source = n.source
    n_other_source = ''    
    if (n.other_source not in ('', None)):
        n_other_source = n.other_source
    n_classification = ''    
    if (n.classification not in ('', None)):
        n_classification = n.classification 
    n_nc_detail_description = ''    
    if (n.nc_detail_description not in ('', None)):
        n_nc_detail_description = n.nc_detail_description
    n_nc_discovered_by = ''    
    if (n.nc_discovered_by not in ('', None)):
        n_nc_discovered_by = n.nc_discovered_by  
    n_nc_conformed_by = ''    
    if (n.nc_conformed_by not in ('', None)):
        n_nc_conformed_by = n.nc_conformed_by      
    nc_conformed_by_chapano = ''
    if nc_conformed_by not in ('', None):
        nc_conformed_by_chapano = nc_conformed_by.chapano
    #B. Immediate Correction     
    n_ic_description = ''    
    if (n.ic_description not in ('', None)):
        n_ic_description = n.ic_description

    n_ic_incharge = ''    
    if (n.ic_incharge not in ('', None)):
        n_ic_incharge = n.ic_incharge  
    ic_incharge_chapano = ''
    if ic_incharge not in ('', None):
        ic_incharge_chapano = ic_incharge.chapano    

    n_ic_approve_by = ''    
    if (n.ic_approve_by not in ('', None)):
        n_ic_approve_by = n.ic_approve_by   
    ic_approve_by_chapano = ''
    if ic_approve_by not in ('', None):
        ic_approve_by_chapano = ic_approve_by.chapano      

    #C. Root Cause Analysis(5 Whys, Fishbone, etc)    
    n_rca_description = ''    
    if (n.rca_description not in ('', None)):
        n_rca_description = n.rca_description
    n_ca_necessary = ''    
    if (n.ca_necessary not in ('', None)):
        n_ca_necessary = n.ca_necessary     
    n_rca_incharge = ''    
    if (n.rca_incharge not in ('', None)):
        n_rca_incharge = n.rca_incharge   
    rca_incharge_chapano = ''
    if rca_incharge not in ('', None):
        rca_incharge_chapano = rca_incharge.chapano  
    n_rca_approve_by = ''    
    if (n.rca_approve_by not in ('', None)):
        n_rca_approve_by = n.rca_approve_by   
    rca_approve_by_chapano = ''
    if rca_approve_by not in ('', None):
        rca_approve_by_chapano = rca_approve_by.chapano  
    
    #D. Corrective Action to the cause
    n_ca_description = ''    
    if (n.ca_description not in ('', None)):
        n_ca_description = n.ca_description
    n_ca_target_date = ''    
    if (n.ca_target_date not in ('', None)):
        n_ca_target_date = n.ca_target_date  
    ca_target_date_str = ''    
    if (ca_target_date not in ('', None)):
        ca_target_date_str = ca_target_date  
    n_ca_approved_by_mgr = ''    
    if (n.ca_approved_by_mgr not in ('', None)):
        n_ca_approved_by_mgr = n.ca_approved_by_mgr      
    ca_approved_by_mgr_chapano = ''
    if ca_approved_by_mgr not in ('', None):
        ca_approved_by_mgr_chapano = ca_approved_by_mgr.chapano
        
    n_ca_checked_by_sh = ''    
    if (n.ca_checked_by_sh not in ('', None)):
        n_ca_checked_by_sh = n.ca_checked_by_sh      
    ca_checked_by_sh_chapano = ''
    if ca_checked_by_sh not in ('', None):
        ca_checked_by_sh_chapano = ca_checked_by_sh.chapano    
        
    #E. Result of action 
    n_ra_description = ''    
    if (n.ra_description not in ('', None)):
        n_ra_description = n.ra_description
    n_ra_action_effective = ''    
    if (n.ra_action_effective not in ('', None)):
        n_ra_action_effective = n.ra_action_effective  
    n_ra_followup_date = ''    
    if (n.ra_followup_date not in ('', None)):
        n_ra_followup_date = n.ra_followup_date  
    ra_followup_date_str = ''    
    if (ra_followup_date not in ('', None)):
        ra_followup_date_str = ra_followup_date      
   
    n_ra_check_by_staff = ''    
    if (n.ra_check_by_staff not in ('', None)):
        n_ra_check_by_staff = n.ra_check_by_staff      
    ra_check_by_staff_chapano = ''
    if ra_check_by_staff not in ('', None):
        ra_check_by_staff_chapano = ra_check_by_staff.chapano      
        
    #F. Show Effectiveness  
    n_se_description = ''    
    if (n.se_description not in ('', None)):
        n_se_description = n.se_description
    n_se_ro_updated = ''    
    if (n.se_ro_updated not in ('', None)):
        n_se_ro_updated = n.se_ro_updated  
    n_se_check_by_qa = ''    
    if (n.se_check_by_qa not in ('', None)):
        n_se_check_by_qa = n.se_check_by_qa     
    se_check_by_qa_chapano = ''
    if se_check_by_qa not in ('', None):
        se_check_by_qa_chapano = se_check_by_qa.chapano
        
    n_ra_check_by_sh = ''    
    if (n.ra_check_by_sh not in ('', None)):
        n_ra_check_by_sh = n.ra_check_by_sh      
    ra_check_by_sh_chapano = ''
    if ra_check_by_sh not in ('', None):
        ra_check_by_sh_chapano = ra_check_by_sh.chapano 
        
    n_se_check_by_mgr = ''    
    if (n.se_check_by_mgr not in ('', None)):
        n_se_check_by_mgr = n.se_check_by_mgr      
    se_check_by_mgr_chapano = ''
    if se_check_by_mgr not in ('', None):
        se_check_by_mgr_chapano = se_check_by_mgr.chapano 

    #A. Nonconformance detail description   
    if n_source != source or n_other_source != other_source or n_classification != classification or n_nc_detail_description != nc_detail_description or n_nc_discovered_by != nc_discovered_by or nc_conformed_by_chapano != n_nc_conformed_by:    
        was_not_changed = False
    
    #B. Immediate Correction
    elif n_ic_description != ic_description or n_ic_incharge != ic_incharge_chapano or n_ic_approve_by != ic_approve_by_chapano:   
        was_not_changed = False
        
    #C. Root Cause Analysis(5 Whys, Fishbone, etc)
    elif n_rca_description != rca_description or n_ca_necessary != ca_necessary or n_rca_incharge != rca_incharge_chapano or n_rca_approve_by != rca_approve_by_chapano:            
        was_not_changed = False
        
    #D. Corrective Action to the cause
    elif n_ca_description != ca_description or n_ca_target_date != ca_target_date_str or n_ca_approved_by_mgr != ca_approved_by_mgr_chapano or n_ca_checked_by_sh != ca_checked_by_sh_chapano:            
        was_not_changed = False
        
    #E. Result of action           
    if n_ra_description != ra_description or n_ra_action_effective != ra_action_effective or n_ra_followup_date != ra_followup_date_str or n_ra_check_by_staff != ra_check_by_staff_chapano:     
        was_not_changed = False
            
    #F. Show Effectiveness  
    if n_se_description != se_description or n_se_ro_updated != se_ro_updated or n_ra_check_by_sh != ra_check_by_sh_chapano or n_se_check_by_mgr != se_check_by_mgr_chapano:            
        was_not_changed = False
    
    #if  se_check_by_qa_chapano != str(n.se_check_by_qa):    
    if se_check_by_qa_chapano != n_se_check_by_qa:        
        was_not_changed = False
    
    if comments != n.comments:        
        was_not_changed = False
    
    print('END: is_error_on_not_changed')    
    return was_not_changed


def is_error_on_required_A(request, form):
    print('START : is_error_on_required_A')
    
    has_error = False
    
    dept = request.POST.get('dept')
    if dept == '':
        has_error = True
        form.fields['dept'].widget.attrs['class'] = "form-control error"
        
    project = request.POST.get('project')
    if project == '':
        has_error = True
        form.fields['project'].widget.attrs['class'] = "form-control error"
        
    ncr_issue_date = form.data.get('ncr_issue_date') 
    if ncr_issue_date == '':
        has_error = True
        form.fields['ncr_issue_date'].widget.attrs['class'] = "form-control error"
    
    source = form.data.get('source')
    if (not source in ('1', '2', '3', '4', '5')):
        has_error = True
        form.fields['source'].widget.attrs['class'] = "form-control radioErr"
    else:   
        other_source = form.data.get('other_source')
        if source == '5' and other_source == '': 
            has_error = True
            form.fields['other_source'].widget.attrs['class'] = "form-control error"
            
    classification = form.data.get('classification')
    if (not classification in ('1', '2')):
        has_error = True
        form.fields['classification'].widget.attrs['class'] = "form-control radioErr"  
     
    nc_detail_description = form.data.get('nc_detail_description')
    if nc_detail_description == '':
        has_error = True
        form.fields['nc_detail_description'].widget.attrs['class'] = "form-control error"
        
    nc_discovered_by = form.data.get('nc_discovered_by')
    if nc_discovered_by == '':
        has_error = True
        form.fields['nc_discovered_by'].widget.attrs['class'] = "form-control error"           
        
    nc_conformed_by = form.data.get('nc_conformed_by')

    if nc_conformed_by == '':
        has_error = True
        form.fields['nc_conformed_by'].widget.attrs['class'] = "form-control error"    

    print('END : is_error_on_required_A')     
    return has_error


def is_error_on_required_B(request, form):
    print('START : is_error_on_required_B')
    
    has_error = False
    
    #B. Immediate Correction 

    ic_description = form.data.get('ic_description')
    if ic_description == '':
        has_error = True
        form.fields['ic_description'].widget.attrs['class'] = "form-control error"    
    
    ic_incharge = form.data.get('ic_incharge')
    if ic_incharge == '':
        has_error = True
        form.fields['ic_incharge'].widget.attrs['class'] = "form-control error"      
        
    
    ic_approve_by = form.data.get('ic_approve_by')
    if ic_approve_by == '':
        has_error = True
        form.fields['ic_approve_by'].widget.attrs['class'] = "form-control error"      

    print('END : is_error_on_required_B')     
    return has_error   


def is_error_on_required_C(request, form):
    print('START : is_error_on_required_C')
    
    has_error = False
    
    #C. Root Cause Analysis(5 Whys, Fishbone, etc)
    
    rca_description = form.data.get('rca_description')
    if rca_description == '':
        has_error = True
        form.fields['rca_description'].widget.attrs['class'] = "form-control error"
        
    #ca_necessary = form.data.get('ca_necessary')
    #if (not ca_necessary in ('0', '1')):
    #    has_error = True
    #    form.fields['ca_necessary'].widget.attrs['class'] = "form-control radioErr"     
    classification = form.data.get('classification')
    if (not classification in ('2')):
        ca_necessary = form.data.get('ca_necessary')
        if (not ca_necessary in ('0', '1')):
            has_error = True
            form.fields['ca_necessary'].widget.attrs['class'] = "form-control radioErr"
    
    rca_incharge = form.data.get('rca_incharge')
    if rca_incharge == '':
        has_error = True
        form.fields['rca_incharge'].widget.attrs['class'] = "form-control error"   
        
    rca_approve_by = form.data.get('rca_approve_by')
    if rca_approve_by == '':
        has_error = True
        form.fields['rca_approve_by'].widget.attrs['class'] = "form-control error"       
        
    print('END : is_error_on_required_C')     
    return has_error  


def is_error_on_required_D(request, form):
    print('START : is_error_on_required_D')
    
    has_error = False
    
    #D. Corrective Action to the cause
    
    ca_description = form.data.get('ca_description')
    if ca_description == '':
        has_error = True
        form.fields['ca_description'].widget.attrs['class'] = "form-control error"
        
    ca_target_date = form.data.get('ca_target_date')
    if ca_target_date == '':
        has_error = True
        form.fields['ca_target_date'].widget.attrs['class'] = "form-control error"  
        
    ca_approved_by_mgr = form.data.get('ca_approved_by_mgr')
    if ca_approved_by_mgr == '':
        has_error = True
        form.fields['ca_approved_by_mgr'].widget.attrs['class'] = "form-control error"    
        
    ca_checked_by_sh = form.data.get('ca_checked_by_sh')
    if ca_checked_by_sh == '':
        has_error = True
        form.fields['ca_checked_by_sh'].widget.attrs['class'] = "form-control error"     

    print('END : is_error_on_required_D')     
    return has_error


def is_error_on_required_E(request, form):
    print('START : is_error_on_required_E')
    
    has_error = False
    
    #E. Result of action   
    ra_description = form.data.get('ra_description')
    if ra_description == '':
        has_error = True
        form.fields['ra_description'].widget.attrs['class'] = "form-control error"
            
    ra_check_by_staff = form.data.get('ra_check_by_staff')
    if ra_check_by_staff == '':
        has_error = True
        form.fields['ra_check_by_staff'].widget.attrs['class'] = "form-control error"    

    ra_check_by_sh = form.data.get('ra_check_by_sh')
    if ra_check_by_sh == '':
        has_error = True
        form.fields['ra_check_by_sh'].widget.attrs['class'] = "form-control error"              
        
    se_check_by_mgr = form.data.get('se_check_by_mgr')
    if se_check_by_mgr == '':
        has_error = True
        form.fields['se_check_by_mgr'].widget.attrs['class'] = "form-control error"    
        
    se_check_by_qa = form.data.get('se_check_by_qa')
    if se_check_by_qa == '':
        has_error = True
        form.fields['se_check_by_qa'].widget.attrs['class'] = "form-control error"  
    
    ra_action_effective = form.data.get('ra_action_effective')
    if ra_action_effective == '2': 
        ra_followup_date = form.data.get('ra_followup_date')
        if ra_followup_date == '': 
            has_error = True
            form.fields['ra_followup_date'].widget.attrs['class'] = "form-control error"    
    
    print('END : is_error_on_required_E')     
    return has_error


def is_error_on_required_F(request, form):
    print('START : is_error_on_required_F')
    
    has_error = False
    
    #F. Show Effectiveness  
                
    se_description = form.data.get('se_description')
    
    if se_description == '':
        has_error = True
        form.fields['se_description'].widget.attrs['class'] = "form-control error"
        
    se_ro_updated = form.data.getlist('se_ro_updated')


    

    #Start adding for Additional Request Edric 2024/02/26
    try:
        if se_ro_updated[0] != '1': #values from checkbox is array type
            se_ro_updated = '0' #from array to string
        else:
            se_ro_updated = '1'
    except:
         print(se_ro_updated)
    #End adding for Additional Request Edric 2024/02/26 
     
    print(se_ro_updated)
    
    if (se_ro_updated not in ('0', '1') or se_ro_updated in ('', 'None')):
        has_error = True

        form.fields['se_ro_updated'].widget.attrs['class'] = "form-control radioErr"    
        

    print('END : is_error_on_required_F')     
    return has_error


def set_dropdowns(form, dept_id):

    sqlStmt = """SELECT e.chapaNo as chapaNo, concat(e.lastName, ', ' ,  e.firstName, ' ' ,  e.middleName) as name
                FROM `RANK` r
                LEFT JOIN EMPLOYEE e ON (r.chapaNo =  e.chapaNo)
                WHERE r.deptId = '"""  + dept_id + """' AND e.status = '1'
                ORDER BY e.lastName ASC"""  
                
    with connection.cursor() as c:
            c.execute(sqlStmt)
            members = namedtuplefetchall(c)                     
            members.insert(0, ['', '---------'])
            form.fields['ic_incharge'].choices = members 
            form.fields['rca_incharge'].choices = members   
            form.fields['ra_check_by_staff'].choices = members   
    
    sqlStmt = """SELECT e.chapaNo as chapaNo, concat(e.lastName, ', ' ,  e.firstName, ' ' ,  e.middleName) as name 
                 FROM ncr_adv_user_tbl n
                     LEFT JOIN EMPLOYEE e ON (n.chapaNo =  e.chapaNo)        
                 WHERE n.dept_id = '""" + dept_id + """'  AND n.user_type IN ('1', '2')
                 ORDER BY n.user_type DESC, e.lastName ASC"""
    
    with connection.cursor() as c:
        c.execute(sqlStmt)
        checkers = namedtuplefetchall(c)           
        checkers.insert(0, ['', '---------'])
        form.fields['nc_conformed_by'].choices = checkers
    
        form.fields['ic_approve_by'].choices = checkers 
        form.fields['rca_approve_by'].choices = checkers 
        form.fields['ca_checked_by_sh'].choices = checkers 
        form.fields['ra_check_by_sh'].choices = checkers 
    
    sqlStmt = """SELECT e.chapaNo as chapaNo, concat(e.lastName, ', ' ,  e.firstName, ' ' ,  e.middleName) as name 
                 FROM ncr_adv_user_tbl n
                     LEFT JOIN EMPLOYEE e ON (n.chapaNo =  e.chapaNo)        
                 WHERE n.dept_id = '""" + dept_id + """'  AND n.user_type = '3'
                 ORDER BY n.user_type DESC, e.lastName ASC"""
 
    with connection.cursor() as c:
        c.execute(sqlStmt)
        mgr_members = namedtuplefetchall(c)                     
        mgr_members.insert(0, ['', '---------'])
        form.fields['ca_approved_by_mgr'].choices = mgr_members
        form.fields['se_check_by_mgr'].choices = mgr_members
    
    sqlStmt = """SELECT e.chapaNo as chapaNo, concat(e.lastName, ', ' ,  e.firstName, ' ' ,  e.middleName) as name
                FROM `RANK` r
                LEFT JOIN EMPLOYEE e ON (r.chapaNo = e.chapaNo)
                WHERE r.deptId = '14' AND e.status = '1' ORDER BY e.lastName ASC"""  
     
    with connection.cursor() as c:
        c.execute(sqlStmt)
        qa_members = namedtuplefetchall(c)                     
        qa_members.insert(0, ['', '---------'])
        form.fields['se_check_by_qa'].choices = qa_members
        
    #sqlStmt = "SELECT p.id AS id, CONCAT(p.code, '::', p.name) AS project_name FROM project p WHERE p.dept_id = '"  + str(dept_id) + "'"     
    sqlStmt = "SELECT p.id AS id, CONCAT(p.code, '::', p.name) AS project_name FROM project p WHERE p.dept_id = '"  + str(dept_id) + "' ORDER BY p.code"
                 
    with connection.cursor() as c:
        c.execute(sqlStmt)
        projects = namedtuplefetchall(c)                     
        projects.insert(0, ['', '---------'])
        form.fields['project'].choices = projects           
          
#Used when link in email is clicked     
def ncr_verify_view_via_mail(request, ncr_no, user_id):
    print('START : ncr_verify_view_via_mail')
    
    login_via_email(request, user_id)
    
    print('END : ncr_verify_view_via_mail')
    return redirect('/ncr/ncr_verify_view/' + ncr_no + '/1/None/None/' + user_id)


def ncr_verify_view(request, ncr_no, check_phase, message, error_message, from_email_id):
    print('START : ncr_verify_view')

    if message == 'None':
        message = ''
        
    if error_message == 'None':
        error_message = ''
    
    form = NCRVerifyForm()
    n = None
    
    nc_conformed_by = ''
    ic_incharge = ''
    ic_approve_by = ''
    rca_incharge = ''
    rca_approve_by = ''
    ca_checked_by_sh = ''
    ca_approved_by_mgr = ''
    ra_check_by_staff = ''
    ra_check_by_sh = ''
    se_check_by_mgr = ''
    se_check_by_qa = ''

    logged_username = 'unknown'
    isChecker = False
    isSH = False    
    isGrpMgr = False
    isAdmin = False
        
    deptId = ''
    
    

    
    current_datetime = datetime.datetime.now()
    #current_datetime = datetime.datetime.now(tz=timezone.utc)
    
    
    
    if 'logged_user_chapa_no' in request.session:
        logged_user_chapa_no = request.session['logged_user_chapa_no']

        if 'logged_username' in request.session:
            logged_username = request.session['logged_username']         
            
        if "logged_user_dept_id" in request.session:    
            logged_user_dept_id = request.session['logged_user_dept_id']      
            
        if 'isChecker' in request.session:    
            isChecker = request.session['isChecker'] 
            
        if 'isSH' in request.session:    
            isSH = request.session['isSH']
            
        if 'isGrpMgr' in request.session:    
            isGrpMgr = request.session['isGrpMgr']
            
        if 'isAdmin' in request.session:    
            isAdmin = request.session['isAdmin']   
            
        deptId = logged_user_dept_id    
    
        #Start adding for additional request Edric Marinas 2024/04/04
        a = ''
    
        try:
            n =  NcrDetailMstr.objects.get(ncr_no=ncr_no)    
            
            
            #Start Edric Marinas 2024/05/08
            array = n.nc_discovered_by.split("||")
            nc_discoverer_email = ''
            try:
                nc_discovered_by = array[0]
                nc_discoverer_email = array[1]
            except:
                pass
            #End
      
        
            try:
                a = DenyReason.objects.get(ncr_no=ncr_no,phase='G')

            except:
                print("No cancel request")    
        #end adding for additional request Edric Marinas 2024/04/04

            deptId = n.dept_id
            
            form = NCRVerifyForm(initial={
                
                
                    #Start adding for additional Request Edric 2024/03/14
                    'hidden_update_user_id' : n.update_user_id,
                    'current_datetime': current_datetime,
                    #End adding for additional Request Edric 2024/03/14
                
                
                    'source' : n.source, 
                    'other_source' : n.other_source, 
                    'classification' : n.classification,  
                    'ic_incharge' : n.ic_incharge,
                    'ca_necessary' : n.ca_necessary,
                    'ra_action_effective' : n.ra_action_effective,
                    'se_ro_updated' : n.se_ro_updated,                    
                    'hidden_update_date' : n.update_date,
                    })
                        
            if n.nc_conformed_by not in (None, ''):
                try:
                    e = Employee.objects.get(chapano=n.nc_conformed_by)
                    nc_conformed_by = e.lastname + ', ' + e.firstname + ' ' + e.middlename
                except Employee.DoesNotExist:
                    error_message = 'Record with chapaNo = doesn''t exist in Employee table.'
                    
            if n.ic_incharge not in (None, ''):
                try:
                    e = Employee.objects.get(chapano=n.ic_incharge)
                    ic_incharge = e.lastname + ', ' + e.firstname + ' ' + e.middlename
                except Employee.DoesNotExist:
                    error_message = 'Record with chapaNo = doesn''t exist in Employee table.'        
               
            if n.ic_approve_by not in (None, ''):
                try:
                    e = Employee.objects.get(chapano=n.ic_approve_by)
                    ic_approve_by = e.lastname + ', ' + e.firstname + ' ' + e.middlename
                except Employee.DoesNotExist:
                    error_message = 'Record with chapaNo = doesn''t exist in Employee table.'
                    
            if n.rca_incharge not in (None, ''):
                try:
                    e = Employee.objects.get(chapano=n.rca_incharge)
                    rca_incharge = e.lastname + ', ' + e.firstname + ' ' + e.middlename
                except Employee.DoesNotExist:
                    error_message = 'Record with chapaNo = doesn''t exist in Employee table.'     
                    
            if n.rca_approve_by not in (None, ''):
                try:
                    e = Employee.objects.get(chapano=n.rca_approve_by)
                    rca_approve_by = e.lastname + ', ' + e.firstname + ' ' + e.middlename
                except Employee.DoesNotExist:
                    error_message = 'Record with chapaNo = doesn''t exist in Employee table.'  
                    
            if n.ca_checked_by_sh not in (None, ''):
                try:
                    e = Employee.objects.get(chapano=n.ca_checked_by_sh)
                    ca_checked_by_sh = e.lastname + ', ' + e.firstname + ' ' + e.middlename
                except Employee.DoesNotExist:
                    error_message = 'Record with chapaNo = doesn''t exist in Employee table.'  
                    
            if n.ca_approved_by_mgr not in (None, ''):
                try:
                    e = Employee.objects.get(chapano=n.ca_approved_by_mgr)
                    ca_approved_by_mgr = e.lastname + ', ' + e.firstname + ' ' + e.middlename
                except Employee.DoesNotExist:
                    error_message = 'Record with chapaNo = doesn''t exist in Employee table.'
                    
            if n.ra_check_by_staff not in (None, ''):
                try:
                    e = Employee.objects.get(chapano=n.ra_check_by_staff )
                    ra_check_by_staff = e.lastname + ', ' + e.firstname + ' ' + e.middlename
                except Employee.DoesNotExist:
                    error_message = 'Record with chapaNo = doesn''t exist in Employee table.'
                    
            if n.ra_check_by_sh not in (None, ''):
                try:
                    e = Employee.objects.get(chapano=n.ra_check_by_sh)
                    ra_check_by_sh = e.lastname + ', ' + e.firstname + ' ' + e.middlename
                except Employee.DoesNotExist:
                    error_message = 'Record with chapaNo = doesn''t exist in Employee table.'
                    
            if n.se_check_by_mgr not in (None, ''):
                try:
                    e = Employee.objects.get(chapano=n.se_check_by_mgr)
                    se_check_by_mgr = e.lastname + ', ' + e.firstname + ' ' + e.middlename
                except Employee.DoesNotExist:
                    error_message = 'Record with chapaNo = doesn''t exist in Employee table.'
                    
            if n.se_check_by_qa not in (None, ''):
                try:
                    e = Employee.objects.get(chapano=n.se_check_by_qa)
                    se_check_by_qa = e.lastname + ', ' + e.firstname + ' ' + e.middlename
                except Employee.DoesNotExist:
                    error_message = 'Record with chapaNo = doesn''t exist in Employee table.'
            
        except NcrDetailMstr.DoesNotExist:
            error_message = 'Record with ncr_no = ' + ncr_no + ' doesn''t exist in NcrDetailMstr table.'
        
        sqlStmt = """SELECT e.chapaNo as chapaNo, concat(e.lastName, ', ' ,  e.firstName, ' ' ,  e.middleName) as name
                FROM `RANK` r
                LEFT JOIN EMPLOYEE e ON (r.chapaNo =  e.chapaNo)
                WHERE r.deptId = '"""  + deptId + """' AND status = '1' ORDER BY e.lastName"""  
                
        with connection.cursor() as c:
            c.execute(sqlStmt)
            members = namedtuplefetchall(c)                     
            members.insert(0, ['', '---------'])
            form.fields['ic_incharge'].choices = members   
    
            form.fields['ic_incharge'].widget.attrs['class'] = "form-control" 
        
        ncr_no_size = 'S'
        if len(n.ncr_no) > 25:     
            ncr_no_size = 'L'
            
            
            
        
        
        
        
        
        context = {
                   #2024/05/08
                   'nc_discovered_by':nc_discovered_by,
                   'nc_discoverer_email':nc_discoverer_email,
                   'form': form, 
                   'a': a,
                   'ncrDetailMstr': n, 
                   'error_message': error_message, 
                   'message' : message,
                   'check_phase' : check_phase,
                   'from_email_id' : from_email_id,
                   'nc_conformed_by' : nc_conformed_by,
                   'ic_incharge' : ic_incharge,
                   'ic_approve_by' : ic_approve_by,
                   'rca_incharge' : rca_incharge,
                   'rca_approve_by' : rca_approve_by,
                   'ca_checked_by_sh' : ca_checked_by_sh,
                   'ca_approved_by_mgr' : ca_approved_by_mgr,
                   'ra_check_by_staff' : ra_check_by_staff,
                   'ra_check_by_sh' : ra_check_by_sh,
                   'se_check_by_mgr' : se_check_by_mgr,
                   'se_check_by_qa' : se_check_by_qa,
                   'logged_username' : logged_username,
                   'isChecker' : isChecker,
                   'isSH' : isSH,
                   'isGrpMgr' : isGrpMgr,
                   'isAdmin' : isAdmin,
                   'ncr_no_size' : ncr_no_size,
                   
                   #Start adding for additional request Edric 2024/03/14
                   'hidden_update_user_id1' : n.update_user_id,
                   #End adding for additional request Edric 2024/03/14
                   
                   
                   'logged_user_chapa_no' : logged_user_chapa_no,                   
                   }
    
        print('END : ncr_verify_view')
        return render(request, 'NCRMgmntSystem/ncr_verify.html', context) 
        #return redirect('/ncr/ncr_verify_view/' + ncr_no + '/1/None/None/' + user_id)
        
    else:
        error_message = 'No user is saved in session.'
        form = LoginForm()
        context = {'form': form, 'error_message': error_message, }    
        print('END : ncr_verify_view')
        return render(request, 'NCRMgmntSystem/login.html', context)          


def ncr_verify_accept(request):
    print('START: ncr_verify_accept')
    
    
    
    ncr_no = request.POST.get('ncrNo', None)
    check_phase = request.POST.get('check_phase', None) 
    from_email_id = request.POST.get('from_email_id', None)     
    hidden_process = request.POST.get('hidden_process', None)
    reason = request.POST.get('reason', None)
    reasonA1 = request.POST.get('reasonA1', None)
    reasonB1 = request.POST.get('reasonB1', None)
    reasonC1 = request.POST.get('reasonC1', None)
    reasonD1 = request.POST.get('reasonD1', None)
    reasonC2 = request.POST.get('reasonC2D2', None)
    reasonE1 = request.POST.get('reasonE1F1', None)
    reasonE2 = request.POST.get('reasonE2F2', None)
    reasonE3 = request.POST.get('reasonE3F3', None)
    process = request.POST.get('process', None)
    
    success_message = ''
    error_message = ''
    db_update_success = False
    send_email_success = False
    logged_user_chapa_no = ''
    n = None

    a = None

    current_datetime = datetime.datetime.now()
    #current_datetime = datetime.datetime.now(tz=timezone.utc)
    
    cancelMessage = request.POST.get('cancelMessage', None)
    
    
    try:
        n =  NcrDetailMstr.objects.get(ncr_no=ncr_no)   
        
    except NcrDetailMstr.DoesNotExist:
        error_message = 'Record with chapaNo = ' + logged_user_chapa_no + ' doesn''t exist in NcrDetailMstr table.'
    
    if 'logged_user_chapa_no' in request.session:
        logged_user_chapa_no = request.session['logged_user_chapa_no'] 

    
     #Start adding due to bug Edric 2024/03/11
    else:
        error_message = 'Can\'t accept/deny. No user is saved in session.'
        context = {'error_message': error_message}
        return render(request, 'NCRMgmntSystem/login.html', context)
    #End adding due to bug Edric 2024/03/11
    


    #set database column 
    n.update_date = current_datetime
    n.update_user_id = logged_user_chapa_no

    
    #Start adding for additional request Edric Marinas 2024/04/04
    if hidden_process == 'denyCancelRequest':
        
        try:
            DenyReason.objects.get(ncr_no=ncr_no,phase='G')
            try:
                cursor=connection.cursor()
                cursor.execute("UPDATE deny_reason SET denied_date = SYSDATE(),reason = '"+reason+"',denied_by = '"+request.session["logged_user_chapa_no"] +"', phase = 'H' WHERE ncr_no = '" + n.ncr_no + "' AND phase='G' ")
                success_message = "Deny cancel request success";
            except DatabaseError:
                print('Error occured while Denying NCR. (NCR#' + ncr_no +')')              
            finally:    
                cursor.close
            
            
            if success_message not in (''):
                print('>>>>>>>>>>>'+str(n))
                sendmail_NCR_cancel_request('0', n)
                #sendmail_NCR_cancel_request('0',n)
                n.status = '4'
                n.save()
                
        except:
            error_message = 'No record'

    
    if hidden_process == 'cancelNCRaccept':
        try:
            try:
                DenyReason.objects.get(ncr_no=ncr_no,phase='G')
                p = 'G'
            except:
                DenyReason.objects.get(ncr_no=ncr_no,phase='H')
                p = 'H'
            try:
                print(">>>>>"+cancelMessage)
                cursor=connection.cursor()
                cursor.execute("UPDATE deny_reason SET denied_date = SYSDATE(),reason = '"+cancelMessage+"',denied_by = '"+request.session["logged_user_chapa_no"] +"',phase ='H' WHERE ncr_no = '" + n.ncr_no + "' AND phase='"+ p +"' ")
                success_message = "NCR cancellation success"
            except DatabaseError:
                error_message = 'Error occured while Denying NCR. (NCR#' + ncr_no +')'

        except DatabaseError:
            error_message = 'Error occured while Denying NCR. (NCR#' + ncr_no +')' 

        except:
            phase = str(declarePhase(n.ncr_no))
            create_cancel_request(n.ncr_no, phase , 'H', cancelMessage, request.session["logged_user_chapa_no"], current_datetime)
            success_message = "NCR cancellation success"

        
        n.status = '2'
        #n.reason = cancelMessage
        n.close_date =  current_datetime
        n.delete_date = current_datetime
        n.delete_user_id = request.session["logged_user_chapa_no"]
        sendmail_ncr_cancelled(n,logged_user_chapa_no)
        n.save()

            

    #End adding for additional request Edric Marinas 2024/04/04

    
    
    
    if hidden_process == 'acceptA1':    
        
        n.ic_incharge = request.POST.get('ic_incharge', None) 
        
        if (n.nc_conformed_by not in (None ,'')):
            if (n.ic_incharge not in (None ,'') ):
                try:
                    e1 =  Employee.objects.get(chapano=n.nc_conformed_by)
                    try:
                         e2 =  Employee.objects.get(chapano=n.ic_incharge)
                         try:
                             sendmail_verify_accept('1', n) 
                             send_email_success = True
                             try:
                                 n.nc_conformed_date = current_datetime
                                 n.nc_conforme_status = 1
                                 n.status = '3' #accepted
                                 
                                 if n.close_date not in ('', None):
                                     n.close_date = None
                                                             
                                 n.save()
                                 db_update_success = True
                                 
                                 try:
                                    cursor=connection.cursor()
                                    cursor.execute("UPDATE deny_reason SET accepted_date = SYSDATE() WHERE ncr_no = '" + n.ncr_no + "' AND rev_no = '" + str(n.rev_no) + "' AND phase = 'A'")
                                 except DatabaseError:
                                    error_message = 'Error occured while inserting NCR data in database. (NCR#' + ncr_no +')'                           
                                 finally:    
                                    cursor.close
                                 
                             except DatabaseError:
                                 error_message = "Database error ocurred while updating data with chapano =  " + n.ncr_no + " in NCR_DETAIL_MSTR table"   
                         except :                                
                             error_message = "There was an error sending an email."
                             
                             
                    except Employee.DoesNotExist:
                         error_message = "Record with chapano =  " + n.ic_incharge + " does not exist in EMPLOYEE table"                                         
                except Employee.DoesNotExist:
                    error_message = "Record with chapano =  " + n.nc_conformed_by + " does not exist in EMPLOYEE table"
            else:    
                error_message = 'In-charge is Null'
        else:
            error_message = 'Conformed By is Null'  
        
    elif hidden_process == 'acceptB1':  
        
        if (n.rca_description in (None ,'')): 
            
            if (n.nc_conformed_by not in (None ,'')):
                if (n.ic_incharge not in (None ,'') ):
                
                    try:
                         e1 =  Employee.objects.get(chapano=n.nc_conformed_by)
                         try:
                             e2 =  Employee.objects.get(chapano=n.ic_incharge)
                             
                             try:
                                 sendmail_verify_accept('7', n) 
                                 send_email_success = True
                                 
                                 try:
                                     n.ic_approve_date = current_datetime
                                     n.ic_approve_status = 1  
                                     #Edric (added n.status= '4')
                                     n.status = '4'
                                     n.save()
                                     db_update_success = True
                                     
                                     try:
                                         cursor=connection.cursor()
                                         cursor.execute("UPDATE deny_reason SET accepted_date = SYSDATE() WHERE ncr_no = '" + n.ncr_no + "' AND rev_no = '" + str(n.rev_no) + "' AND phase = 'B'")
                                     except DatabaseError:
                                         error_message = 'Error occured while inserting NCR data in database. (NCR#' + ncr_no +')'                           
                                     finally:    
                                         cursor.close
                            
                                 except DatabaseError:
                                     error_message = "Database error ocurred while updating data with chapano =  " + n.ncr_no + " in NCR_DETAIL_MSTR table"   
                            
                             except SMTPException:                                
                                 error_message = "There was an error sending an email."
                            
                         except Employee.DoesNotExist:
                             error_message = "Record with chapano =  " + n.ic_incharge + " does not exist in EMPLOYEE table"                
                            
                    except Employee.DoesNotExist:
                        error_message = "Record with chapano =  " + n.nc_conformed_by + " does not exist in EMPLOYEE table"
                else:    
                    error_message = 'ic_incharge is Null'
            else:
                error_message = 'nc_conformed_by is Null'   
            
        else:    
            if (n.ic_approve_by not in (None ,'')):
                try:
                    e1 =  Employee.objects.get(chapano=n.ic_approve_by)
                
                    try:
                        n.ic_approve_date = current_datetime
                        n.ic_approve_status = 1
                        #Edric (added n.status= '4')
                        n.status = '4'
                        n.save()
                        db_update_success = True
                            
                        if n.ic_approve_date not in (None, '') and n.rca_approve_date not in (None, '') and n.ca_check_date_by_sh not in (None, ''):
                            try:
                                sendmail_verify_accept('2', n)    
                                send_email_success = True
                                
                                try:
                                    cursor=connection.cursor()
                                    cursor.execute("UPDATE deny_reason SET accepted_date = SYSDATE() WHERE ncr_no = '" + n.ncr_no + "' AND rev_no = '" + str(n.rev_no) + "' AND phase = 'B'")
                                except DatabaseError:
                                    error_message = 'Error occured while inserting NCR data in database. (NCR#' + ncr_no +')'                           
                                finally:    
                                     cursor.close
                                         
                            except SMTPException:
                                error_message = "There was an error sending an email."  
    
                    except DatabaseError:
                        error_message = "Database error ocurred while updating data with chapano =  " + n.ncr_no + " in NCR_DETAIL_MSTR table"                           
                    
                except Employee.DoesNotExist:
                    error_message = "Record with chapano =  " + n.ic_approve_by + " does not exist in EMPLOYEE table"
            else:
                error_message = 'ic_approve_by'    
            
    elif hidden_process == 'acceptC1':  
        #Start added n.ca_necessary == "0" due to bug Edric 2024/04/11 When CA necessary is no it wont close the NCR if there is value on step D
        if (n.ca_necessary == "0" or n.ca_description in (None ,'') ): 
            
            if n.ca_necessary == "1":
                if (n.nc_conformed_by not in (None ,'')):
                    if (n.ic_incharge not in (None ,'') ):            
                        try:
                             e1 =  Employee.objects.get(chapano=n.nc_conformed_by)
                             try:
                                 e2 =  Employee.objects.get(chapano=n.ic_incharge)
                                 try:
                                     sendmail_verify_accept('C-Yes', n) 
                                     send_email_success = True

                                     try:
                                         n.rca_approve_date = current_datetime    
                                         n.rca_approve_status = 1
                                         n.close_date = None
                                         n.status = '4' #on-going
                                         n.save()
                                         db_update_success = True

                                         try:
                                             cursor=connection.cursor()
                                             cursor.execute("UPDATE deny_reason SET accepted_date = SYSDATE() WHERE ncr_no = '" + n.ncr_no + "' AND rev_no = '" + str(n.rev_no) + "' AND phase = 'C'")
                                         except DatabaseError:
                                             error_message = 'Error occured while inserting NCR data in database. (NCR#' + ncr_no +')'                           
                                         finally:    
                                             cursor.close
                                     
                                     except DatabaseError:
                                         error_message = "Database error ocurred while updating data with chapano =  " + n.ncr_no + " in NCR_DETAIL_MSTR table"   
                            
                                 except SMTPException:                                
                                     error_message = "There was an error sending an email."
                            
                             except Employee.DoesNotExist:
                                 error_message = "Record with chapano =  " + n.ic_incharge + " does not exist in EMPLOYEE table"                
                            
                        except Employee.DoesNotExist:
                            error_message = "Record with chapano =  " + n.nc_conformed_by + " does not exist in EMPLOYEE table"
                    else:    
                        error_message = 'In-Charge for C. Corrective Action is Null'
                else:
                    error_message = 'Approved by for C. Corrective Action is null'  

            elif n.ca_necessary == "0":
                
                if (n.nc_conformed_by not in (None ,'')):
                    if (n.ic_incharge not in (None ,'') ):            
                        try:
                             e1 =  Employee.objects.get(chapano=n.nc_conformed_by)
                             try:
                                 e2 =  Employee.objects.get(chapano=n.ic_incharge)
                                 try:
                                     sendmail_verify_accept('C-No', n) 
                                     send_email_success = True
                                    
                                     try:
                                         n.rca_approve_date = current_datetime    
                                         n.rca_approve_status = 1
                                         n.close_date = current_datetime
                                         n.status = '5' #closed
                                         
                                         n.save()
                                         db_update_success = True
                                         
                                         try:
                                             cursor=connection.cursor()
                                             cursor.execute("UPDATE deny_reason SET accepted_date = SYSDATE() WHERE ncr_no = '" + n.ncr_no + "' AND rev_no = '" + str(n.rev_no) + "' AND phase = 'C'")
                                         except DatabaseError:
                                             error_message = 'Error occured while inserting NCR data in database. (NCR#' + ncr_no +')'                           
                                         finally:    
                                             cursor.close
                                             
                                     except DatabaseError:
                                         error_message = "Database error ocurred while updating data with chapano =  " + n.ncr_no + " in NCR_DETAIL_MSTR table"   
                            
                                 except SMTPException:                                
                                     error_message = "There was an error sending an email."
                            
                             except Employee.DoesNotExist:
                                 error_message = "Record with chapano =  " + n.ic_incharge + " does not exist in EMPLOYEE table"                
                            
                        except Employee.DoesNotExist:
                            error_message = "Record with chapano =  " + n.nc_conformed_by + " does not exist in EMPLOYEE table"
                    else:    
                        error_message = 'In-Charge for C. Corrective Action is Null'
                else:
                    error_message = 'Approved by for C. Corrective Action is Null'  
              
        else:   
            
            
            if (n.rca_approve_by not in (None ,'')):
                try:
                    e1 =  Employee.objects.get(chapano=n.rca_approve_by)
                
                    try:
                        n.rca_approve_date = current_datetime
                        n.rca_approve_status = 1
                        n.close_date = None
                        n.status = '4' #on-going
                        n.save()
                        db_update_success = True
                        
                        if n.rca_approve_date not in (None, '') and n.ca_check_date_by_sh not in (None, ''):    
                            try:
                                sendmail_verify_accept('2', n)    
                                send_email_success = True
                                
                                try:
                                    cursor=connection.cursor()
                                    cursor.execute("UPDATE deny_reason SET accepted_date = SYSDATE() WHERE ncr_no = '" + n.ncr_no + "' AND rev_no = '" + str(n.rev_no) + "' AND phase = 'C'")
                                except DatabaseError:
                                    error_message = 'Error occured while inserting NCR data in database. (NCR#' + ncr_no +')'                           
                                finally:    
                                    cursor.close
                                             
                            except SMTPException:
                                error_message = "There was an error sending an email."
                        
                        #start added by ROS 20220608 when CA approver is different with RCA approver
                        elif n.rca_approve_date not in (None, '') and n.ca_checked_by_sh != n.rca_approve_by:
                            try:
                                sendmail_verify_accept('4', n)    
                                send_email_success = True
                                
                                try:
                                    cursor=connection.cursor()
                                    cursor.execute("UPDATE deny_reason SET accepted_date = SYSDATE() WHERE ncr_no = '" + n.ncr_no + "' AND rev_no = '" + str(n.rev_no) + "' AND phase = 'C'")
                                except DatabaseError:
                                    error_message = 'Error occured while inserting NCR data in database. (NCR#' + ncr_no +')'                           
                                finally:    
                                    cursor.close
                                             
                            except SMTPException:
                                error_message = "There was an error sending an email."
                        #start added by ROS 20220608                        
    
                    except DatabaseError:
                        error_message = "Database error ocurred while updating data with chapano =  " + n.ncr_no + " in NCR_DETAIL_MSTR table"                           
                    
                except Employee.DoesNotExist:
                    error_message = "Record with chapano =  " + n.rca_approve_by + " does not exist in EMPLOYEE table"
            else:
                error_message = 'rca_approve_by'            
            
    #elif request.POST.get('acceptD1',None):
    elif hidden_process == 'acceptD1':      
        
        if (n.ca_checked_by_sh not in (None ,'')):
            try:
                e1 =  Employee.objects.get(chapano=n.ca_checked_by_sh)
                
                try:
                    n.ca_check_date_by_sh = current_datetime
                    n.ca_check_by_sh_status = 1
                    #Edric (added n.status= '4')
                    n.status = '4'
                    n.save()
                    db_update_success = True
                    
                    if str(n.rca_approve_status) == '1' and str(n.ca_check_by_sh_status) == '1':        
                        try:
                            sendmail_verify_accept('2', n) 
                            send_email_success = True
                            try:
                                cursor=connection.cursor()
                                cursor.execute("UPDATE deny_reason SET accepted_date = SYSDATE()  WHERE ncr_no = '" + n.ncr_no + "' AND rev_no = '" + str(n.rev_no) + "' AND phase = 'D'" )
                            except DatabaseError:
                                error_message = 'Error occured while inserting NCR data in database. (NCR#' + ncr_no +')'                           
                            finally:    
                                cursor.close
                                             
                        except SMTPException:   
                            error_message = "There was an error sending an email."  

                except DatabaseError:
                    error_message = "Database error ocurred while updating data with chapano =  " + n.ncr_no + " in NCR_DETAIL_MSTR table"                           
                    
            except Employee.DoesNotExist:
                error_message = "Record with chapano =  " + n.ca_checked_by_sh + " does not exist in EMPLOYEE table"
        else:
            error_message = 'Checked By for D. Corrective Action is null'         

    elif hidden_process == 'acceptC2D2':     
        try:
            sendmail_verify_accept('3', n) 
            send_email_success = True
            try:
                n.ca_approved_date_by_mgr = current_datetime   
                n.rca_approve_status = 1
                n.ca_check_by_sh_status = 1
                n.ca_approve_by_mgr_status = 1
                #Edric (added n.status= '4')
                n.status = '4'
                n.save()
                db_update_success = True

                try:
                    cursor=connection.cursor()
                    cursor.execute("UPDATE deny_reason SET accepted_date = SYSDATE() WHERE ncr_no = '" + n.ncr_no + "' AND rev_no = '" + str(n.rev_no) + "' AND phase = 'D'")
                except DatabaseError:
                    error_message = 'Error occured while inserting NCR data in database. (NCR#' + ncr_no +')'                           
                finally:    
                    cursor.close

            except DatabaseError:
                error_message = "Database error ocurred while updating data with chapano =  " + n.ncr_no + " in NCR_DETAIL_MSTR table"   
        except SMTPException:                                
            error_message = "There was an error sending an email."  
        
    elif hidden_process == 'acceptE1F1':      
        try:
            sendmail_verify_accept('acceptE', n) 
            send_email_success = True

            try:
                n.ra_check_date_by_sh = current_datetime
                n.rca_approve_status = 1
                n.ca_check_by_sh_status = 1
                n.ca_approve_by_mgr_status = 1
                n.ra_check_by_sh_status = 1  
                #Edric (added n.status= '4')
                n.status = '4'
                n.save()
                db_update_success = True
  
                try:
                    cursor=connection.cursor()
                    cursor.execute("UPDATE deny_reason SET accepted_date = SYSDATE() WHERE ncr_no = '" + n.ncr_no + "' AND rev_no = '" + str(n.rev_no) + "' AND phase = 'E'")
                except DatabaseError:
                    error_message = 'Error occured while inserting NCR data in database. (NCR#' + ncr_no +')'                           
                finally:    
                    cursor.close
                                             
            except DatabaseError:
                error_message = "Database error ocurred while updating data with chapano =  " + n.ncr_no + " in NCR_DETAIL_MSTR table"   
                    
        except SMTPException:                                
            error_message = "There was an error sending an email."  
            
    elif hidden_process == 'acceptE2F2':  
        
        if (n.se_check_by_mgr not in (None ,'')):
            if (n.se_check_by_qa not in (None ,'')):
                try:
                    e1 =  Employee.objects.get(chapano=n.se_check_by_mgr)
                    try:
                        e2 =  Employee.objects.get(chapano=n.se_check_by_qa)

                        try:
                            n.se_check_date_by_mgr = current_datetime
                            n.rca_approve_status = 1
                            n.ca_check_by_sh_status = 1
                            n.ca_approve_by_mgr_status = 1
                            n.ra_check_by_sh_status = 1  
                            n.se_check_by_mgr_status = 1
                            #Edric (added n.status= '4')
                            n.status = '4'
                            n.save()
                            db_update_success = True

                            try:
                                sendmail_verify_accept('5', n) 
                                send_email_success = True

                                try:
                                    cursor=connection.cursor()
                                    cursor.execute("UPDATE deny_reason SET accepted_date = SYSDATE() WHERE ncr_no = '" + n.ncr_no + "' AND rev_no = '" + str(n.rev_no) + "' AND phase = 'F'")
                                except DatabaseError:
                                    error_message = 'Error occured while inserting NCR data in database. (NCR#' + ncr_no +')'                           
                                finally:    
                                    cursor.close
                            
                            except SMTPException:                                
                                error_message = "There was an error sending an email."  
    
                        except DatabaseError:
                            error_message = "Database error ocurred while updating data with chapano =  " + n.ncr_no + " in NCR_DETAIL_MSTR table"   
                        
                    except Employee.DoesNotExist:
                        error_message = "Record with chapano =  " + n.se_check_by_qa + " does not exist in EMPLOYEE table"                
                except Employee.DoesNotExist:
                    error_message = "Record with chapano =  " + n.se_check_by_mgr + " does not exist in EMPLOYEE table"
            else:    
                error_message = 'se_check_by_qa'
        else:
            error_message = 'se_check_by_mgr'
            
    elif hidden_process == 'acceptE3F3':  
        
        if (n.se_check_by_qa not in (None ,'')):
            if (n.ic_incharge not in (None ,'')):
                try:
                    e1 =  Employee.objects.get(chapano=n.se_check_by_qa)
                    try:
                        e2 =  Employee.objects.get(chapano=n.ic_incharge)
                        
                        try:
                            n.se_check_date_by_qa = current_datetime
                            n.rca_approve_status = 1
                            n.ca_check_by_sh_status = 1
                            n.ca_approve_by_mgr_status = 1
                            n.ra_check_by_sh_status = 1  
                            n.se_check_by_mgr_status = 1
                            n.se_check_by_qa_status = 1
                            n.close_date = current_datetime
                            n.status = '5' #closed
                            n.save()
                            db_update_success = True
                            
                            try:
                                sendmail_verify_accept('6', n)  
                                send_email_success = True
                                
                                try:
                                    cursor=connection.cursor()
                                    cursor.execute("UPDATE deny_reason SET accepted_date = SYSDATE() WHERE ncr_no = '" + n.ncr_no + "' AND rev_no = '" + str(n.rev_no) + "' AND phase = 'F'")
                                except DatabaseError:
                                    error_message = 'Error occured while inserting NCR data in database. (NCR#' + ncr_no +')'                           
                                finally:    
                                    cursor.close
                            
                            except SMTPException:                                
                                error_message = "There was an error sending an email."  
    
                        except DatabaseError:
                            error_message = "Database error ocurred while updating data with chapano =  " + n.ncr_no + " in NCR_DETAIL_MSTR table"   
                        
                    except Employee.DoesNotExist:
                        error_message = "Record with chapano =  " + n.ic_incharge + " does not exist in EMPLOYEE table"                
                except Employee.DoesNotExist:
                    error_message = "Record with chapano =  " + n.se_check_by_qa + " does not exist in EMPLOYEE table"
            else:    
                error_message = 'ic_incharge'
        else:
            error_message = 'se_check_by_mgr'

    #elif process == 'denyA1':
    elif hidden_process == 'denyA1':    
        
        print('hidden_process >>>> ' + str(hidden_process))
        
        #error_message = create_deny_reason(n.ncr_no, n.rev_no, "A", reasonA1, n.nc_conformed_by, current_datetime)
        error_message = create_deny_reason(n.ncr_no, n.rev_no, "A", reason, n.nc_conformed_by, current_datetime)
        
        if error_message in ('', None):
            #create NCR_DETAIL_MSTR table
            try:
                n.nc_conforme_status = '0'
                n.nc_conformed_date = current_datetime
                n.status = '1' #issued
                n.save()   
                db_update_success = True
                
                error_message = sendmail_verify_deny(n.ncr_no, n.nc_conformed_by, n.ncr_issue_by, "A")
                
                if error_message in ('', None):
                    send_email_success = True            
                
            except DatabaseError:
                error_message = "Database error ocurred while updating data with ncr_no =  " + n.ncr_no + " in NCR_DETAIL_MSTR table"  
    
    #Added 2024/04/2
    #elif process == 'cancelNCR':
    elif hidden_process == 'cancelNCR': 
        
        #error_message = create_deny_reason(n.ncr_no, n.rev_no, "", reasonA1, n.nc_conformed_by, current_datetime)
        error_message = create_deny_reason(n.ncr_no, n.rev_no, "", reason, n.nc_conformed_by, current_datetime)
        
        if error_message in ('', None):
            #create NCR_DETAIL_MSTR table
            try:
                n.close_date = current_datetime
                n.status = '2' #cancelled
                n.nc_conforme_status = None
                n.save()   
                db_update_success = True
                
                error_message = sendmail_verify_deny(n.ncr_no, n.nc_conformed_by, n.ncr_issue_by, "X")
                
                if error_message in ('', None):
                    send_email_success = True            
                
            except DatabaseError:
                error_message = "Database error ocurred while updating data with ncr_no =  " + n.ncr_no + " in NCR_DETAIL_MSTR table"
    
    #elif process == 'denyB1': 
    elif hidden_process == 'denyB1':     
        
        print('hidden_process >>>> ' + str(hidden_process))
        
        #error_message = create_deny_reason(n.ncr_no, n.rev_no, "B", reasonB1, n.ic_approve_by, current_datetime)
        error_message = create_deny_reason(n.ncr_no, n.rev_no, "B", reason, n.ic_approve_by, current_datetime)
        
        if error_message in ('', None):
            #create NCR_DETAIL_MSTR table
            try:
                n.ic_approve_status = '0'
                n.ic_approve_date = current_datetime
                n.update_date = current_datetime   
                n.update_user_id = logged_user_chapa_no
                n.status = '4'
                n.save()   
                db_update_success = True
                
                error_message = sendmail_verify_deny(n.ncr_no, n.ic_approve_by, n.ic_incharge, "B")
                if error_message in ('', None):
                    send_email_success = True                 
                    
            except DatabaseError:
                error_message = "Database error ocurred while updating data with ncr_no =  " + n.ncr_no + " in NCR_DETAIL_MSTR table"  
        
    #elif process == 'denyC1':
    elif hidden_process == 'denyC1': 
        
        print('hidden_process >>>> ' + str(hidden_process))
        
        
        
        #Start adding due to bug Edric Marinas 2024/02/22
        n.status = '4'
        if n.status not in ('',None): 
            n.close_date = None
        #End adding due to bug Edric Marinas 2024/02/22
            
            
        #error_message = create_deny_reason(n.ncr_no, n.rev_no, "C", reasonC1, n.rca_approve_by, current_datetime)
        error_message = create_deny_reason(n.ncr_no, n.rev_no, "C", reason, n.rca_approve_by, current_datetime)
            
        if error_message in ('', None):
            #create NCR_DETAIL_MSTR table
            try:
                n.rca_approve_status = '0'
                n.rca_approve_date = current_datetime
                
                if n.ca_description not in ('', None): 
                    n.ca_check_by_sh_status = '0'
                    n.ca_check_date_by_sh = current_datetime
                
                n.save()   
                db_update_success = True
                
                if n.ca_description not in ('', None):  
                    error_message = sendmail_verify_deny(n.ncr_no, n.rca_approve_by, n.rca_incharge, "C&D")
                else: 
                    error_message = sendmail_verify_deny(n.ncr_no, n.rca_approve_by, n.rca_incharge, "C")
                    
                if error_message in ('', None):
                    send_email_success = True                     
                    
            except DatabaseError:
                error_message = "Database error ocurred while updating data with ncr_no =  " + n.ncr_no + " in NCR_DETAIL_MSTR table"    
    
    #elif process == 'denyD1':
    elif hidden_process == 'denyD1':     
        
        print('hidden_process >>>> ' + str(hidden_process))
        
        #error_message = create_deny_reason(n.ncr_no, n.rev_no, "C", reasonD1, n.ca_checked_by_sh, current_datetime)
        
        
        
        #Start modify Edric  2024/03/21
        #error_message = create_deny_reason(n.ncr_no, n.rev_no, "C", reason, n.ca_checked_by_sh, current_datetime)
        error_message = create_deny_reason(n.ncr_no, n.rev_no, "D", reason, n.ca_checked_by_sh, current_datetime) 
        #End modify Edric  2024/03/21  
        if error_message in ('', None):
            #create NCR_DETAIL_MSTR table
            try:
                n.ca_check_by_sh_status = '0'
                n.ca_check_date_by_sh = current_datetime
                n.save()   
                db_update_success = True
                
                error_message = sendmail_verify_deny(n.ncr_no, n.ca_checked_by_sh, n.ca_create_by, "C&D")
                if error_message in ('', None):
                    send_email_success = True       
                    
            except DatabaseError:
                error_message = "Database error ocurred while updating data with ncr_no =  " + n.ncr_no + " in NCR_DETAIL_MSTR table"  
        
    #elif process == 'denyC2D2':
    elif hidden_process == 'denyC2D2':     
        
        
        
        #error_message = create_deny_reason(n.ncr_no, n.rev_no, "C", reasonC2, n.ca_approved_by_mgr, current_datetime) 
        
        #Start modify Edric  2024/03/21
        #error_message = create_deny_reason(n.ncr_no, n.rev_no, "C", reason, n.ca_approved_by_mgr, current_datetime)
        error_message = create_deny_reason(n.ncr_no, n.rev_no, "D", reason, n.ca_approved_by_mgr, current_datetime) 
        #End modify Edric  2024/03/21    
        if error_message in ('', None):
            #create NCR_DETAIL_MSTR table
            try:
                n.rca_approve_status = '0'
                n.rca_approve_date = current_datetime
                n.ca_check_by_sh_status = '0'
                n.ca_check_date_by_sh = current_datetime
                n.ca_approve_by_mgr_status = '0'
                n.ca_approved_date_by_mgr = current_datetime
                n.save()   
                db_update_success = True
                
                error_message = sendmail_verify_deny(n.ncr_no, n.ca_approved_by_mgr, n.ca_create_by, "C&D")
                if error_message in ('', None):
                    send_email_success = True   
                    
            except DatabaseError:
                error_message = "Database error ocurred while updating data with ncr_no =  " + n.ncr_no + " in NCR_DETAIL_MSTR table"     
                
    #elif process == 'denyE1F1':
    elif hidden_process == 'denyE1F1':     
        #error_message = create_deny_reason(n.ncr_no, n.rev_no, "E", reasonE1, n.ra_check_by_sh, current_datetime)
        error_message = create_deny_reason(n.ncr_no, n.rev_no, "E", reason, n.ra_check_by_sh, current_datetime)
        
        if error_message in ('', None):
            #create NCR_DETAIL_MSTR table
            try:
                n.rca_approve_status = '0'
                n.rca_approve_date = current_datetime
                n.ca_check_by_sh_status = '0'
                n.ca_check_date_by_sh = current_datetime
                n.ca_approve_by_mgr_status = '0'
                n.ca_approved_date_by_mgr = current_datetime
                n.ra_check_by_sh_status = '0'
                n.ra_check_date_by_sh = current_datetime
                
                n.save()   
                db_update_success = True
                
                if n.se_description not in ('', None):  
                    error_message = sendmail_verify_deny(n.ncr_no, n.ra_check_by_sh, n.ra_check_by_staff, "C&D&E&F")
                else: 
                    error_message = sendmail_verify_deny(n.ncr_no, n.ra_check_by_sh, n.ra_check_by_staff, "C&D&E")
                    
                
                if error_message in ('', None):
                    send_email_success = True     
                    
            except DatabaseError:
                error_message = "Database error ocurred while updating data with ncr_no =  " + n.ncr_no + " in NCR_DETAIL_MSTR table"             
          
    #elif process == 'denyE2F2':
    elif hidden_process == 'denyE2F2':     
        #error_message = create_deny_reason(n.ncr_no, n.rev_no, "E", reasonE2, n.se_check_by_mgr, current_datetime)
        error_message = create_deny_reason(n.ncr_no, n.rev_no, "E", reason, n.se_check_by_mgr, current_datetime)
        
        if error_message in ('', None):
            #create NCR_DETAIL_MSTR table
            try:
                n.rca_approve_status = '0'
                n.rca_approve_date = current_datetime
                n.ca_check_by_sh_status = '0'
                n.ca_check_date_by_sh = current_datetime
                n.ca_approve_by_mgr_status = '0'
                n.ca_approved_date_by_mgr = current_datetime
                n.ra_check_by_sh_status = '0'
                n.ra_check_date_by_sh = current_datetime
                n.se_check_by_mgr_status = '0'
                n.se_check_date_by_mgr = current_datetime
                n.save()   
                db_update_success = True
                
                if n.se_description not in ('', None):  
                    error_message = sendmail_verify_deny(n.ncr_no, n.se_check_by_mgr, n.ra_check_by_staff, "C&D&E&F")
                else: 
                    error_message = sendmail_verify_deny(n.ncr_no, n.se_check_by_mgr, n.ra_check_by_staff, "C&D&E")
                    
                if error_message in ('', None):
                    send_email_success = True    
                    
            except DatabaseError:
                error_message = "Database error ocurred while updating data with ncr_no =  " + n.ncr_no + " in NCR_DETAIL_MSTR table"             
            
    #elif process == 'denyE3F3':
    elif hidden_process == 'denyE3F3':     
        #error_message = create_deny_reason(n.ncr_no, n.rev_no, "E", reasonE3, n.se_check_by_qa, current_datetime)
        error_message = create_deny_reason(n.ncr_no, n.rev_no, "E", reason, n.se_check_by_qa, current_datetime)
        
        if error_message in ('', None):
            #create NCR_DETAIL_MSTR table
            try:
                n.rca_approve_status = '0'
                n.rca_approve_date = current_datetime
                n.ca_check_by_sh_status = '0'
                n.ca_check_date_by_sh = current_datetime
                n.ca_approve_by_mgr_status = '0'
                n.ca_approved_date_by_mgr = current_datetime
                n.ra_check_by_sh_status = '0'
                n.ra_check_date_by_sh = current_datetime
                n.se_check_by_mgr_status = '0'
                n.se_check_date_by_mgr = current_datetime
                n.se_check_by_qa_status = '0'
                n.se_check_date_by_qa = current_datetime
                n.status = '4' #on-going
                
                if n.close_date not in ('', None):
                    n.close_date = None
                
                n.save()   
                db_update_success = True
                
                if n.se_description not in ('', None):  
                    error_message = sendmail_verify_deny(n.ncr_no, n.se_check_by_qa, n.ra_check_by_staff, "C&D&E&F")
                else: 
                    error_message = sendmail_verify_deny(n.ncr_no, n.se_check_by_qa, n.ra_check_by_staff, "C&D&E")
                    
                if error_message in ('', None):
                    send_email_success = True    
                    
            except DatabaseError:
                error_message = "Database error ocurred while updating data with ncr_no =  " + n.ncr_no + " in NCR_DETAIL_MSTR table"             
    
    if error_message in (None, ''):
        if db_update_success and send_email_success:
            success_message = 'NCR data was successfully updated and email notification was sent.'  
        elif db_update_success:
            success_message = 'NCR data was successfully updated.'
        
        error_message = 'None'
    else:         
        success_message = 'None'
    
    print('END: ncr_verify_accept')
    return redirect('/ncr/ncr_verify_view/' + ncr_no + '/' +  check_phase + '/' + success_message + '/' + error_message + '/' + from_email_id)


def create_deny_reason(ncr_no, rev_no, step, reason, deny_by, deny_date):
    error_message = ""
    
    try:
        cursor=connection.cursor()      
        cursor.execute("INSERT INTO deny_reason(ncr_no, rev_no, phase, reason, denied_by, denied_date) VALUES('" + ncr_no + "', '" + str(rev_no) + "', '" + step + "', '" + str(reason) + "', '" + deny_by + "', '" + str(deny_date) +  "')")    
        
    except IntegrityError as e:
        print(e)
        cursor.execute("UPDATE deny_reason SET denied_by = '" + deny_by + "', denied_date = SYSDATE(), reason = '" + str(reason) + "', accepted_date = null WHERE ncr_no = '" + ncr_no + "' AND rev_no = '" + str(rev_no) + "' AND phase = '" + step + "'")                    
    except DatabaseError as e:
        print(e)
        error_message = "Error occured while inserting DENY_REASON data in database."                           
    finally:    
        cursor.close
    
    return error_message


def sendmail_create(mailType, n):
    subject = 'NCR Create Status Notification: ' + str(n.ncr_no)       
    from_email = 'NCR_Mgnt_Sys@shi-g.com'
    send_to = ''  
    content = ''
    
    if mailType == 'A':
        e =  Employee.objects.get(chapano=n.nc_conformed_by)
        send_to = e.email
        user_id = e.chapano
        content = "Sir/Madam,\n\n    A Nonconformance has been issued in your section. Kindly confirm by clicking\non the link below to proceed with NCR process.\n\n    Please accomplish necessary action and verify effectiveness within 2 weeks\nfor Minor NC or 1 month for Major NC.\n\n    " + PROJ_URL + "ncr_verify_view_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply."  
        
    elif mailType == 'B':
        e =  Employee.objects.get(chapano=n.ic_approve_by)
        send_to = e.email
        user_id = e.chapano
        content = "Sir/Madam,\n\n    Immediate correction was performed. Kindly confirm\ncontent for approval by clicking on the link below to proceed to next step.\n\n    " + PROJ_URL + "ncr_verify_view_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply."
    
    elif mailType == 'C-Yes':
        e =  Employee.objects.get(chapano=n.rca_approve_by)
        send_to = e.email
        user_id = e.chapano
        content = "Sir/Madam,\n\n    A Nonconformance has been analyzed. Kindly confirm\ncontent for approval by clicking on the link below to proceed to next step.\n\n    " + PROJ_URL + "ncr_verify_view_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply."

    elif mailType == 'C-No':
        e =  Employee.objects.get(chapano=n.rca_approve_by)
        send_to = e.email
        user_id = e.chapano
        content = "Sir/Madam,\n\n    A Nonconformance has been analyzed and found that corrective action was not necessary\n and is requesting for NCR closing. Kindly confirm the effectiveness\nby clicking on the link below to close this NCR.\n\n    " + PROJ_URL + "ncr_verify_view_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply."

    elif mailType == 'D':
        #modified by ROS 2022/06/08
        #e =  Employee.objects.get(chapano=n.ic_approve_by)
        e =  Employee.objects.get(chapano=n.ca_checked_by_sh)
        send_to = e.email
        user_id = e.chapano
        content = "Sir/Madam,\n\n    A Nonconformance corrective action was set. Kindly confirm\n content for approval by clicking on the link below to proceed to next step.\n\n    " + PROJ_URL + "ncr_verify_view_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply."

    elif mailType == 'C&D':
        #modified by ROS 2022/06/08
        #e =  Employee.objects.get(chapano=n.ic_approve_by)
        e =  Employee.objects.get(chapano=n.rca_approve_by) 

        user_id = e.chapano
    
    
        send_to = e.email
        content = "Sir/Madam,\n\n    A Nonconformance has been analyzed and corrective action was set. Kindly confirm\ncontent for approval by clicking on the link below to proceed to next step.\n\n    " + PROJ_URL + "ncr_verify_view_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply."


        
    elif mailType == 'E-returnToC':
        e =  Employee.objects.get(chapano=n.rca_approve_by)
        send_to = e.email
        user_id = e.chapano
        content = "Sir/Madam,\n\n    Previous corrective action was not effective. New analysis and corrective action was set. Kindly confirm\ncontent for approval by clicking below button.\n\n    " + PROJ_URL + "ncr_verify_view_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply."

    elif mailType == 'E-proceedToF':
        e =  Employee.objects.get(chapano=n.ra_check_by_sh)
        send_to = e.email
        user_id = e.chapano
        content = "Sir/Madam,\n\n    Result Of Action and its Effectiveness has been accomplished. Kindly confirm its result and effectiveness\nby clicking on the link below to close this NCR.\n\n    " + PROJ_URL + "ncr_verify_view_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply."
        
    elif mailType == 'E':
        e =  Employee.objects.get(chapano=n.ra_check_by_sh)
        send_to = e.email
        user_id = e.chapano
        content = "Sir/Madam,\n\n    Result Of Action has been accomplished. Kindly confirm its result by clicking on the \nlink below to close this NCR.\n\n    " + PROJ_URL + "ncr_verify_view_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply."

    elif mailType == 'F':
        if (n.se_check_by_mgr_status == '1'): 
            e =  Employee.objects.get(chapano=n.se_check_by_qa)  
        else:    
            e =  Employee.objects.get(chapano=n.ra_check_by_sh)
        
        send_to = e.email
        user_id = e.chapano
        content = "Sir/Madam,\n\n    Effectiveness of action has been accomplished. Kindly confirm the effectiveness\nby clicking on the link below to close this NCR.\n\n    " + PROJ_URL + "ncr_verify_view_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply."  
    
    

    elif mailType == 'C_approved-y/n':
        #e =  Employee.objects.get(chapano=n.rca_approve_by) 
        #user_id = e.chapano
        
        if n.rca_approve_date != None: #C approved is true
            e =  Employee.objects.get(chapano=n.ca_checked_by_sh)#send mail to CA-SH
            user_id = e.chapano
            send_to = e.email
            content = "Sir/Madam,\n\n        The In charge notified you, Kindly confirm by clicking on the link below to proceed with next step.\n\n    " + PROJ_URL + "ncr_create_view_upd_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply."

        else: #C approved is false
            e =  Employee.objects.get(chapano=n.rca_approve_by)#send mail to RCA-Approver in case In charge sent notify while RCA is already approved
            user_id = e.chapano
            send_to = e.email
            user_id = e.chapano
            content = "Sir/Madam,\n\n    A Nonconformance corrective action was set. Kindly confirm\n content for approval by clicking on the link below to proceed to next step.\n\n    " + PROJ_URL + "ncr_verify_view_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply."

    #send email
    try:
        for x in send_to:
            send_mail(subject, content, from_email, [x], fail_silently=False,)
            
    except:
        send_mail(subject, content, from_email, [send_to, ], fail_silently=False,)

    return   
 
# Send mail for NCOA02 screen 
def sendmail_verify_accept(mailType, n):
    subject = 'NCR Accept Status Notification: '  + str(n.ncr_no)       
    from_email = 'NCR_Mgnt_Sys@shi-g.com'


    
    
    #Start modify for additional request Edric Charles C. Marinas 2024/03/04
     
    '''if mailType == '1':
        e1 =  Employee.objects.get(chapano=n.nc_conformed_by)
        e2 =  Employee.objects.get(chapano=n.ic_incharge)
        send_to = e2.email
        user_id = e2.chapano
        content = "Sir/Madam,\n\n        Issued NCR registered " + n.ncr_no + " had been accepted by " + e1.lastname + ", " + e1.firstname + " " + e1.middlename + ".\n\n    Kindly confirm by clicking on the link below to proceed with next step.\n\n    " + PROJ_URL + "ncr_create_view_upd_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply."         
        send_mail(subject, content, from_email, [send_to], fail_silently=False,)'''
        
        
    if mailType == '1':

        send_to = ''
        try:
            e =  Employee.objects.get(chapano=n.nc_conformed_by)
            #send_to = e.email
            #user_id = e.chapano
            #content = "Sir/Madam,\n\n    A Nonconformance has been issued in your section. Kindly confirm by clicking\non the link below to proceed with NCR process.\n\n    Please accomplish necessary action and verify effectiveness within 2 weeks\nfor Minor NC or 1 month for Major NC.\n\n    " + PROJ_URL + "ncr_verify_view_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply."  
            #send_mail(subject, content, from_email, [send_to], fail_silently=False,)
        

        except:
            print("ERROR 1")
        
        #Added Edric Marinas 2024/05/08 
        
        
        #Discovered By 2024/05/08
        
        
        try:
            array = n.nc_discovered_by.split("||")
            send_to = str(array[1])
            rev = str(n.rev_no)

            content = "Sir/Madam,\n\n    A Nonconformance has been issued in your section. Kindly confirm by clicking\non the link below to proceed with NCR process.\n\n    Please accomplish necessary action and verify effectiveness within 2 weeks\nfor Minor NC or 1 month for Major NC.\n\n    " + PROJ_URL + "ncr_create_view_history/" + n.ncr_no + "/" + rev + "/view\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply."
            send_mail(subject, content, from_email, [send_to], fail_silently=False,)
            print("(Discovered By) Email sent to  Email: "+  send_to)
            print( PROJ_URL + "ncr_create_view_history/" + n.ncr_no + "/" + rev + "/#")
        except:
            pass
            
        
        #End    
            
        try:
            e = Employee.objects.get(chapano=n.ic_incharge)
            send_to = e.email
            user_id = e.chapano
            content = "Sir/Madam,\n\n    A Nonconformance has been issued in your section. Kindly confirm by clicking\non the link below to proceed with NCR process.\n\n    Please accomplish necessary action and verify effectiveness within 2 weeks\nfor Minor NC or 1 month for Major NC.\n\n    " + PROJ_URL + "ncr_create_view_upd_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply."  
            send_mail(subject, content, from_email, [send_to], fail_silently=False,)
            print("(in charge) Email sent to ChapaNo: " + e.chapano +" Email: "+  send_to)
        except:
            print("ERROR 2")
       
        """try :
            send_to.append(discoverer_email)

        except:
            print("error")"""
            
        try:    

            #GRP MANAGER            
            sqlStmt = """
                      SELECT e.chapaNo as chapano, concat(e.lastName, ', ' ,  e.firstName, ' ' ,  e.middleName) as name, e.email as email
                      FROM `ncr_adv_user_tbl` ncr
                      LEFT JOIN EMPLOYEE e ON (ncr.chapaNo = e.chapaNo)
                      WHERE e.status = '1' AND ncr.dept_id = '"""+n.dept_id +"""' AND ncr.user_type = '3'
                      """  
                         
                         

            with connection.cursor() as c:
                c.execute(sqlStmt)
                members = namedtuplefetchall(c)  
            for x in members:
                send_to = x.email
                user_id = x.chapano
                content = "Sir/Madam,\n\n    A Nonconformance has been issued in your section. Kindly confirm by clicking\non the link below to proceed with NCR process.\n\n    Please accomplish necessary action and verify effectiveness within 2 weeks\nfor Minor NC or 1 month for Major NC.\n\n    " + PROJ_URL + "ncr_verify_view_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply."  
                send_mail(subject, content, from_email, [send_to], fail_silently=False,)
                print("(Grp manager) Email sent to ChapaNo: " + x.chapano +" Email: "+ send_to)
        except:
            print("ERROR 3")



        try: 
        #QA MEMBERS
            sql = """SELECT n.chapano AS chapano, e.email AS email, e.firstname AS firstname FROM ncr_adv_user_tbl n, employee e 
                  WHERE e.chapano = n.chapano AND n.user_type = '4'"""
            
            
            with connection.cursor() as c:
                c.execute(sql)
                
                qa_mgrs = namedtuplefetchall(c)                     
    
            for qa_mgr in qa_mgrs:
                send_to = qa_mgr.email
                user_id = qa_mgr.chapano

                content = "Sir/Madam,\n\n    A Nonconformance has been issued in your section. Kindly confirm by clicking\non the link below to proceed with NCR process.\n\n    Please accomplish necessary action and verify effectiveness within 2 weeks\nfor Minor NC or 1 month for Major NC.\n\n    " + PROJ_URL + "ncr_verify_view_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply."  
                send_mail(subject, content, from_email, [send_to], fail_silently=False,)
                print("(QA members) Email sent to ChapaNo: " +qa_mgr.chapano +" Email: "+qa_mgr.email)
        except:
            print("ERROR 4")
        
                #send_to = e.email
                
        #End modify for additional request Edric Charles C. Marinas 2024/03/04
        
        
        
        
    elif mailType == '2':
        
        
        
        e1 =  Employee.objects.get(chapano=n.ca_checked_by_sh)
        e2 =  Employee.objects.get(chapano=n.ca_approved_by_mgr)
        send_to = e2.email
        user_id = e2.chapano
        
        
        if n.ca_checked_by_sh != n.rca_approve_by:
            e3 =  Employee.objects.get(chapano=n.rca_approve_by)
            
            content = "Sir/Madam, "+ e2.firstname +"\n\n        The content of root cause analysis has been accepted by " +  e3.lastname + ", " + e3.firstname + " " + e3.middlename +"  and corrective action had been analyzed and \n\n accepted by " +  e1.lastname + ", " + e1.firstname + " " + e1.middlename + ".\n\n    Kindly confirm content for your approval by clicking on the link below.\n\n    " + PROJ_URL + "ncr_verify_view_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply."
        else:
            content = "Sir/Madam,\n\n        The content of root cause analysis and corrective action had been analyzed and \n\n accepted by " +  e1.lastname + ", " + e1.firstname + " " + e1.middlename + ".\n\n    Kindly confirm content for your approval by clicking on the link below.\n\n    " + PROJ_URL + "ncr_verify_view_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply."
        
        send_mail(subject, content, from_email, [send_to], fail_silently=False,)    
       
        
       
    elif mailType == '3':
        e1 =  Employee.objects.get(chapano=n.ca_approved_by_mgr)
        e2 =  Employee.objects.get(chapano=n.ic_incharge)
        send_to = e2.email
        user_id = e2.chapano

        content = "Sir/Madam,\n\n        The content of root cause analysis and corrective action had been analyzed and \n\n accepted by Grp Mgr: " +  e1.lastname + ", " + e1.firstname + " " + e1.middlename + ".\n\n    Kindly confirm by clicking on the link below to proceed with the next step.\n\n    " + PROJ_URL + "ncr_create_view_upd_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply."
        send_mail(subject, content, from_email, [send_to], fail_silently=False,)  
    
    elif mailType == 'acceptE':
        e1 =  Employee.objects.get(chapano=n.ra_check_by_sh)
        e2 =  Employee.objects.get(chapano=n.se_check_by_mgr)
        send_to = e2.email
        user_id = e2.chapano
    
        if n.se_description not in ('', None):
            content = "Sir/Madam,\n\n        The result and effectiveness of corrective action had been analyzed and accepted by " +  e1.lastname + ", " + e1.firstname + " " + e1.middlename + ".\n\n    Kindly confirm content for approval by clicking on the link below.\n\n    " + PROJ_URL + "ncr_verify_view_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply."
        else:
            content = "Sir/Madam,\n\n        The result of corrective action had been analyzed and accepted by " +  e1.lastname + ", " + e1.firstname + " " + e1.middlename + ".\n\n    Kindly confirm content for approval by clicking on the link below.\n\n    " + PROJ_URL + "ncr_verify_view_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply."
        
        send_mail(subject, content, from_email, [send_to], fail_silently=False,)  
    
    elif mailType == '5':
        e1 =  Employee.objects.get(chapano=n.se_check_by_mgr)
        
        if (n.classification == '1'  or (n.classification == '2' and n.se_description not in ('', None) and n.se_ro_updated == '1')):
            e2 =  Employee.objects.get(chapano=n.se_check_by_qa)
            send_to = e2.email
            user_id = e2.chapano
            content = "Sir/Madam,\n\n        The result and effectiveness of corrective action had been analyzed and accepted by Grp Mgr: " +  e1.lastname + ", " + e1.firstname + " " + e1.middlename + ".\n\n and is requesting to close this NCR.\n\n    Kindly confirm content for approval by clicking on the link below.\n\n    " + PROJ_URL + "ncr_verify_view_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply."
            
        elif (n.classification == '2' and n.se_description not in ('', None) and n.se_ro_updated != '1'):
            e2 =  Employee.objects.get(chapano=n.ra_check_by_staff)
            send_to = e2.email
            user_id = e2.chapano 
            content = "Sir/Madam,\n\n        The result and effectiveness of corrective action had been analyzed and accepted by\n\n Grp Mgr: " +  e1.lastname + ", " + e1.firstname + " " + e1.middlename + ", but your Risk and Oppurtunity is not yet updated.\n\n    Kindly update your Risk and Oppurtunity before QA checking.\n\n     " + PROJ_URL + "ncr_create_view_upd_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply."
        


        send_mail(subject, content, from_email, [send_to], fail_silently=False,)  
        
        
        
        
    elif mailType == '6':
        send_to = ''
        
        #Start Modifying for additional request Edric Charles Marinas 2024.03.06
        #sql = "Select archive_location, name FROM project WHERE dept_id = '" + n.dept_id + "' AND id = '" + n.project_id + "'"
        
           
        
        
        sql = "Select archive_location, name FROM project WHERE dept_id = '" + str(n.dept_id) + "' AND id = '" + str(n.project_id) + "'"
        with connection.cursor() as c:
            c.execute(sql)
            nxt = c.fetchone()

        try:
            #QA 
            e1 =  Employee.objects.get(chapano=n.se_check_by_qa)

            #send_to = e1.email
            #user_id = qa_mgr.chapano
            #content = "Sir/Madam,\n\n    A Nonconformance has been issued in your section. Kindly confirm by clicking\non the link below to proceed with NCR process.\n\n    Please accomplish necessary action and verify effectiveness within 2 weeks\nfor Minor NC or 1 month for Major NC.\n\n    " + PROJ_URL + "ncr_verify_view_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply."  
            #send_mail(subject, content, from_email, [send_to], fail_silently=False,)
        except:
            print("ERROR 6-1")
        
        try:
            #In-charge
            e2 =  Employee.objects.get(chapano=n.ra_check_by_staff)
            send_to = e2.email
            user_id = e2.chapano
            content = "Sir/Madam,\n\n        This NCR was closed by QA Mgr: " +  e1.lastname + ", " + e1.firstname + " " + e1.middlename + " and will be compiled in NCR Archive\n\n    of " + nxt[1] + ".\n\n     Location: " + nxt[0] + "\n\n    Kindly confirm by clicking on link below.\n\n    " + PROJ_URL + "ncr_create_view_upd_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply."
            send_mail(subject, content, from_email, [send_to], fail_silently=False,)
            print("Email sent to ChapaNo: " + e2.chapano +" Email: "+  send_to)
        except:
            print("ERROR 6-2")
            
        #Discovered By 2024/05/08
        try:
            array = n.nc_discovered_by.split("||")
            send_to = str(array[1])
            rev = str(n.rev_no)

            content = "Sir/Madam,\n\n    This NCR was closed by QA Mgr: " +  e1.lastname + ", " + e1.firstname + " " + e1.middlename + ".\n\n    and will be compiled in NCR Archive\n\n    of " + nxt[1] + ".\n\n     Location: " + nxt[0] + "\n\n   Kindly confirm by clicking on link below.\n\n" + PROJ_URL + "ncr_create_view_history/" + n.ncr_no + "/" + rev + "/view\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply."
            send_mail(subject, content, from_email, [send_to], fail_silently=False,)
            print("(Discovered By) Email sent to Email: "+  send_to)

        except:
            pass
        #End 



        try:
            #SH
            e3 =  Employee.objects.get(chapano=n.ra_check_by_sh)
            send_to = e3.email 
            user_id = e3.chapano
            content = "Sir/Madam,\n\n        This NCR was closed by QA Mgr: " +  e1.lastname + ", " + e1.firstname + " " + e1.middlename + " and will be compiled in NCR Archive\n\n    of " + nxt[1] + ".\n\n     Location: " + nxt[0] + "\n\n    Kindly confirm by clicking on link below.\n\n    " + PROJ_URL + "ncr_verify_view_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply."
            send_mail(subject, content, from_email, [send_to], fail_silently=False,)
            print("Email sent to ChapaNo: " + e3.chapano +" Email: "+  send_to)
        except:
            print("ERROR 6-3")
        
        try:
            #Grp Mgr
            e4 =  Employee.objects.get(chapano=n.se_check_by_mgr)
            send_to = e4.email 
            user_id = e4.chapano
            content = "Sir/Madam,\n\n        This NCR was closed by QA Mgr: " +  e1.lastname + ", " + e1.firstname + " " + e1.middlename + " and will be compiled in NCR Archive\n\n    of " + nxt[1] + ".\n\n     Location: " + nxt[0] + "\n\n    Kindly confirm by clicking on link below.\n\n    " + PROJ_URL + "ncr_verify_view_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply."
            send_mail(subject, content, from_email, [send_to], fail_silently=False,)
            print("Email sent to ChapaNo: " + e4.chapano +" Email: "+  send_to)
        except:
            print("ERROR 6-4")
        
        
        sql = """SELECT n.chapano AS chapano, e.email AS email FROM ncr_adv_user_tbl n, employee e 
              WHERE e.chapano = n.chapano AND n.user_type = '4'"""
     
        with connection.cursor() as c:
            c.execute(sql)
            qa_mgrs = namedtuplefetchall(c)                     
          
        for qa_mgr in qa_mgrs:
            
            send_to = qa_mgr.email
            user_id = qa_mgr.chapano
            content = "Sir/Madam,\n\n        This NCR was closed by QA Mgr: " +  e1.lastname + ", " + e1.firstname + " " + e1.middlename + " and will be compiled in NCR Archive\n\n    of " + nxt[1] + ".\n\n     Location: " + nxt[0] + "\n\n    Kindly confirm by clicking on link below.\n\n    " + PROJ_URL + "ncr_verify_view_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply."
            if n.se_check_by_qa != user_id:
                send_mail(subject, content, from_email, [send_to], fail_silently=False,)
                print("Email sent to ChapaNo: " + qa_mgr.chapano +" Email: "+  send_to)
        
        #send_mail(subject, content, from_email, send_to, fail_silently=False,)
        
        #End Modifying for additional request Edric Charles Marinas 2024.03.06
        
          
    
    elif mailType == '7':
        e1 =  Employee.objects.get(chapano=n.nc_conformed_by)
        e2 =  Employee.objects.get(chapano=n.ic_incharge)
        send_to = e2.email
        user_id = e2.chapano
        content = "Sir/Madam,\n\n        The content of immediate correction had been approved by " + e1.lastname + ", " + e1.firstname + " " + e1.middlename + ".\n\n    Kindly confirm by clicking on the link below to proceed with next step.\n\n    " + PROJ_URL + "ncr_create_view_upd_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply."        
        
        send_mail(subject, content, from_email, [send_to], fail_silently=False,)
        
    elif mailType == 'C-Yes':
        
        e1 =  Employee.objects.get(chapano=n.rca_approve_by)
        e2 =  Employee.objects.get(chapano=n.rca_incharge)
        send_to = e2.email        
        user_id = e2.chapano
        content = "Sir/Madam,\n\n        The content of root cause analysis had been approved by " + e1.lastname + ", " + e1.firstname + " " + e1.middlename + ".\n\n    Kindly confirm by clicking on the link below to proceed with next step.\n\n    " + PROJ_URL + "ncr_create_view_upd_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply."        
        send_mail(subject, content, from_email, [send_to], fail_silently=False,)
    
    elif mailType == 'C-No':
        #Start modify due to bugs Edric 02/20/2024
        send_to = ''   
        
        
        
        #sql = "Select archive_location, name FROM project WHERE dept_id = '" + n.dept_id + "' AND id = '" + n.project_id + "'"
        sql = "Select archive_location, name FROM project WHERE dept_id = '" + str(n.dept_id) + "' AND id = '" + str(n.project_id) + "'"
        with connection.cursor() as c:
            c.execute(sql)
            nxt = c.fetchone()
  
        try:
            #SH, DSH, TH or Asst TH
            e1 =  Employee.objects.get(chapano=n.rca_approve_by)
        except:
            print("ERROR C-no 1")

        try:
            #In-charge
            e2 =  Employee.objects.get(chapano=n.rca_incharge)
            send_to = e2.email
            user_id = e2.chapano
            content = "Sir/Madam,\n\n        This NCR even without corrective action was closed by " +  e1.lastname + ", " + e1.firstname + " " + e1.middlename + " and will be compiled in NCR Archive\n\n    of " + str(nxt[1]) + ".\n\n     Location: " + str(nxt[0]) + "\n\n    Kindly confirm by clicking on link below.\n\n    " + PROJ_URL + "ncr_create_view_upd_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply."
            send_mail(subject, content, from_email, [send_to], fail_silently=False,)
            
        except:
            print("ERROR C-no 2")
        
        
        #Discovered By 2024/05/08
        try:
            array = n.nc_discovered_by.split("||")
            send_to = str(array[1])
            rev = str(n.rev_no)

            content = "Sir/Madam,\n\n    This NCR even without corrective action was closed by " +  e1.lastname + ", " + e1.firstname + " " + e1.middlename + ".\n\n    and will be compiled in NCR Archive\n\n    of " + nxt[1] + ".\n\n     Location: " + nxt[0] + "\n\n   Kindly confirm by clicking on link below.\n\n" + PROJ_URL + "ncr_create_view_history/" + n.ncr_no + "/" + rev + "/view\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply."
            send_mail(subject, content, from_email, [send_to], fail_silently=False,)
            print("(Discovered By) Email sent to   Email: "+  send_to)

        except:
            pass
        #End
        
        
        
        
        try:
            #SQL to acquire QA Managers - NOTE: user_type = '4' (QA Manager)  
            sql = """SELECT n.chapano AS chapano, e.email AS email FROM ncr_adv_user_tbl n, employee e 
                  WHERE e.chapano = n.chapano AND n.user_type = '4'"""
         
            with connection.cursor() as c:
                c.execute(sql)
                qa_mgrs = namedtuplefetchall(c)                     
              
            for qa_mgr in qa_mgrs:
                send_to = qa_mgr.email
                user_id = qa_mgr.chapano
                content = "Sir/Madam,\n\n        This NCR even without corrective action was closed by " +  e1.lastname + ", " + e1.firstname + " " + e1.middlename + " and will be compiled in NCR Archive\n\n    of " + str(nxt[1]) + ".\n\n     Location: " + str(nxt[0]) + "\n\n    Kindly confirm by clicking on link below.\n\n    " + PROJ_URL + "ncr_verify_view_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply."
                send_mail(subject, content, from_email, [send_to], fail_silently=False,)
                
            #SQL to acquire Archiving info
            
        except:
            print("ERROR C-no 3")
        #End modify due to bugs Edric 02/20/2024



    #start added by ROS 20220608
    #when approver set in RCA is different with approver set in Corrective Action
    elif mailType == '4':
        e1 =  Employee.objects.get(chapano=n.rca_approve_by)
        e2 =  Employee.objects.get(chapano=n.ca_checked_by_sh)
        send_to = e2.email
        user_id = e2.chapano
        content = "Sir/Madam,\n\n        The content of root cause analysis has been analyzed and accepted by " +  e1.lastname + ", " + e1.firstname + " " + e1.middlename + ".\n\n    Kindly confirm by clicking on the link below to proceed with the next step.\n\n    " + PROJ_URL + "ncr_verify_view_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply."
        send_mail(subject, content, from_email, [send_to], fail_silently=False,)
    #end added by ROS 20220608    
        
    return 

# Send mail for NCOA02 screen 
def sendmail_verify_deny(ncr_no, checker_id, in_charged_id, rejectedStage,):
    print('START: sendmail_verify_deny')
    error_message = ''
    subject = 'NCR Deny Status Notification: ' + str(ncr_no)        
    from_email = 'NCR_Mgnt_Sys@shi-g.com'
    send_to = ''  
    content = ''
    rejectedStageTitle = ''
    
        
    
    try:
        e1 =  Employee.objects.get(chapano=checker_id)
        
        try:
            e2 =  Employee.objects.get(chapano=in_charged_id)
            
            if rejectedStage == "A":
                rejectedStageTitle = "A. Nonconformance Detail Description"        
            elif rejectedStage == "B":    
                rejectedStageTitle = "B. Immediate Correction"        
            elif rejectedStage == "C&D":        
                rejectedStageTitle = "C. Root Cause Analysis and D. Corrective Action"        
            elif rejectedStage == "C":        
                rejectedStageTitle = "C. Root Cause Analysis"        
            elif rejectedStage == "D":        
                rejectedStageTitle = "D. Corrective Action"        
            elif rejectedStage == "E&F":        
                rejectedStageTitle = "E. Result Of Action and F. Show Effectiveness"        
            elif rejectedStage == "E":        
                rejectedStageTitle = "E. Result Of Action"        
            elif rejectedStage == "F": 
                rejectedStageTitle = "F. Show Effectiveness"  
            elif rejectedStage == "C&D&E":        
                rejectedStageTitle = "C. Root Cause Analysis, D. Corrective Action and E. Result Of Action and F. Show Effectiveness"  
            elif rejectedStage == "C&D&E&F":        
                rejectedStageTitle = "C. Root Cause Analysis, D. Corrective Action, E. Result Of Action and F. Show Effectiveness"      
    
            send_to = e2.email
            user_id = e2.chapano
            
            if "X" == rejectedStage:
                content = "Sir/Madam,\n\n        The NCR registered " + ncr_no + " had been cancelled by " + e1.lastname + ", " + e1.firstname + " " + e1.middlename + ".\n\n    Kindly confirm by clicking on the link below to make your correction.\n\n     " + PROJ_URL + "ncr_create_view_upd_via_mail/" + ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply."         
            else:
                content = "Sir/Madam,\n\n        The content of " + rejectedStageTitle + " had been rejected by " + e1.lastname + ", " + e1.firstname + " " + e1.middlename + ".\n\n    Kindly confirm by clicking on the link below to make your correction.\n\n     " + PROJ_URL + "ncr_create_view_upd_via_mail/" + ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply."       
       
            try:
                send_mail(subject, content, from_email, [send_to], fail_silently=False,)
            except SMTPException as e:                                
                error_message = "There was an error sending an email." + e
            
        except NcrDetailMstr.DoesNotExist:
            error_message = 'Record with chapaNo =  ' + in_charged_id + ' doesn''t exist in Employee table.'    
        
    except NcrDetailMstr.DoesNotExist:
        error_message = 'Record with chapaNo =  ' + checker_id + ' doesn''t exist in Employee table.'
        
    print('END: sendmail_verify_deny')
    return error_message 


def namedtuplefetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


def load_projects(request):
    dept_id = request.GET.get('dept')    
    try:
        projects = Project.objects.filter(dept_id=dept_id).order_by('name')
    except:
        print("DEPT ID IS NONE")
        projects = Project.objects.filter().order_by('name')
    
        
    
    
    
    return render(request, 'NCRMgmntSystem/projects_dropdown_list_options.html', {'projects': projects}) 


def load_members(request):
    dept_id = request.GET.get('dept')
    sqlStmt = """SELECT e.chapaNo as chapano, concat(e.lastName, ', ' ,  e.firstName, ' ' ,  e.middleName) as name
                 FROM `RANK` r
                 LEFT JOIN EMPLOYEE e ON (r.chapaNo = e.chapaNo)
                 WHERE r.deptId = '""" + dept_id + """' AND status = '1'"""  
    with connection.cursor() as c:
        c.execute(sqlStmt)
        members = namedtuplefetchall(c)                     
    return render(request, 'NCRMgmntSystem/members_dropdown_list_options.html', {'members': members}) 


def load_checkers(request):
    dept_id = request.GET.get('dept')
    sqlStmt = """SELECT e.chapaNo as chapano, concat(e.lastName, ', ' ,  e.firstName, ' ' ,  e.middleName) as name 
                 FROM ncr_adv_user_tbl n
                     LEFT JOIN EMPLOYEE e ON (n.chapaNo =  e.chapaNo)        
                 WHERE n.dept_id = '""" + dept_id + """'  AND n.user_type IN ('1', '2')
                 ORDER BY n.user_type DESC, n.chapano ASC"""
    with connection.cursor() as c:
        c.execute(sqlStmt)
        checkers = namedtuplefetchall(c)    
    return render(request, 'NCRMgmntSystem/checkers_dropdown_list_options.html', {'checkers': checkers}) 


def ncr_create(request):
    print('START : ncr_create')
    

    deny_reasonA = request.POST.get('deny_reasonA', '')
    deny_reasonB = request.POST.get('deny_reasonB', '')
    deny_reasonC = request.POST.get('deny_reasonC', '')
    deny_reasonD = request.POST.get('deny_reasonD', '')
    deny_reasonE = request.POST.get('deny_reasonE', '')
    deny_reasonF = request.POST.get('deny_reasonF', '')
        
    nc_conformed_by_name = request.POST.get('nc_conformed_by_name', '')    
    ic_approve_by_name = request.POST.get('ic_approve_by_name', '')  
    rca_approve_by_name = request.POST.get('rca_approve_by_name', '')
    ca_checked_by_sh_name = request.POST.get('ca_checked_by_sh_name', '') 
    ra_check_by_sh_name = request.POST.get('ra_check_by_sh_name', '')            
    ic_incharge_name = request.POST.get('ic_incharge_name', '')
    rca_incharge_name = request.POST.get('rca_incharge_name', '')
    ra_check_by_staff_name = request.POST.get('ra_check_by_staff_name', '')
    ca_approved_by_mgr_name = request.POST.get('ca_approved_by_mgr_name', '')
    se_check_by_mgr_name = request.POST.get('se_check_by_mgr_name', '')
    
    #Edric 
    S_or_SN = request.POST.get('S_or_SN', '')
    nc_discoverer_email = request.POST.get('nc_discoverer_email', '')

    
    
    form = None
    error_message = ''
    n = None
    db_transact = '#'
    hidden_dept_id = ''
    logged_user_chapa_no = 'XXX'
    
    if "logged_user_chapa_no" in request.session:
        logged_user_chapa_no = request.session["logged_user_chapa_no"] 
        
        if "logged_username" in request.session:
            logged_username = request.session["logged_username"]         
            
        if "isChecker" in request.session:    
            isChecker = request.session["isChecker"] 
            
        if "isSH" in request.session:    
            isSH = request.session["isSH"]
            
        if "isGrpMgr" in request.session:    
            isGrpMgr = request.session["isGrpMgr"]
            
        if "isAdmin" in request.session:    
            isAdmin = request.session["isAdmin"]    
            
    else:
        form = LoginForm() 
        context = {'form': form}  
        print('END: ncr_create')
        return render(request, 'NCRMgmntSystem/login.html', context)  
    
    edit_cause = '0'
    
    if request.method != 'POST':
        raise Http404('Only POSTs are allowed')
    else:
        form = NCRCreateForm(request.POST or None)   
    
    ncr_no = form.data.get('ncr_no') 
    reason_action_not_effective = form.data.get('reason_action_not_effective') 
    
    
    
    
    
    
    if is_error_on_required(request, form):    
        error_message = 'Highlighted fields are required.'
    
    is_form_valid = False
    send_email_success = True
    
    if error_message in ('', None): 
        if form.is_valid():
            is_form_valid = True;
            
            ncr_no = form.cleaned_data['ncr_no']           
        
            if ncr_no not in [None, '']:
                
                db_transact = 'U' #update 
            
                try:
                    n =  NcrDetailMstr.objects.get(ncr_no=ncr_no)     
                    
                    if is_error_on_not_changed(request, form):
                        error_message = 'No changes was made.' 
                        
                    else:
                        reason_action_not_effective = form.cleaned_data['reason_action_not_effective']     
                    
                        if reason_action_not_effective not in ('', None):
                            #return_to_C (action not effective)
                            edit_cause = '2' 
                    
                            #archive current NCR
                            try:
                                cursor=connection.cursor()
                                #copy current NCR to archive
                                cursor.execute("INSERT INTO ncr_detail_mstr_history SELECT * FROM ncr_detail_mstr WHERE ncr_no = '" + n.ncr_no + "'")
                                #set E info to database
                                cursor.execute("UPDATE ncr_detail_mstr_history SET ra_action_effective = '1', ra_check_by_staff_status = '0', ra_check_date_by_staff = SYSDATE(), ra_check_by_staff = '" + 
                                           logged_user_chapa_no + "', ra_description = '" + reason_action_not_effective + "' WHERE ncr_no = '" + n.ncr_no + "' AND rev_no = '" + str(n.rev_no) + "'")
                                
                                try:
                                    ncr_create_update(request, form, ncr_no, logged_user_chapa_no, edit_cause)                            
                                except DatabaseError:
                                    
                                    #db_update_success = False
                                    error_message = 'Error occured while updating NCR data in database. (NCR#' + ncr_no +')'       
                                    
                                except SMTPException:   
                                    send_email_success = False
                                    error_message = "There was an error sending an email."     
                    
                            except IntegrityError:
                                error_message = 'Error occured while inserting NCR data in database. (Duplicate Entry - NCR#' + ncr_no +')'       
                                
                            except DatabaseError:

                                error_message = 'Error occured while inserting NCR data in database. (NCR#' + ncr_no +')'   
                                
                            finally:    
                                cursor.close
                        
                        else:
                            #check if NCR was denied    
                            deny_cnt = 0
                            sqlStmt = "SELECT count(*) as cnt FROM DENY_REASON WHERE ncr_no = '" + n.ncr_no + "' AND rev_no = '" + str(n.rev_no) + "'"     

                            with connection.cursor() as c:
                                c.execute(sqlStmt)
                                result = c.fetchone()
                                deny_cnt = result[0]

                            #if denied NCR, archive it
                            if deny_cnt > 0:      
                                #inputs denied 
                                edit_cause = '1'

                                try:

                                    cursor=connection.cursor()
                                    
                                    
                                    cursor.execute("INSERT INTO ncr_detail_mstr_history SELECT * FROM ncr_detail_mstr WHERE ncr_no = '" + ncr_no + "'");


                                except IntegrityError:

                                    error_message = 'Error occured while inserting NCR data in database. (Duplicate Entry - NCR#' + ncr_no +')'       

                                except DatabaseError:
                                    error_message = 'Error occured while inserting NCR data in database. (NCR# '+ncr_no+') '

                                finally:    
                                    cursor.close
                             
                            try:

                                n = ncr_create_update(request, form, ncr_no, logged_user_chapa_no, edit_cause)   

                                if n.classification == '2' and n.se_description in ('', None) and n.ra_description not in ('', None) :      
                                    send_email_success = False

                            except DatabaseError:
                                error_message = 'Error occured while updating NCR data in database. (NCR#' + ncr_no +')'       
    
                            except SMTPException:   
                                send_email_success = False
                                error_message = "There was an error sending an email."        
                
                except NcrDetailMstr.DoesNotExist:
                    error_message = "Record with NCR#" + ncr_no + "does not exist in NCR_DETAIL_MSTR!"
            
            else:
                db_transact = 'I' #insert 

                try:
                    
                    n = ncr_create_insert(request, form, logged_user_chapa_no)  
                    ncr_no = n.ncr_no

                    
                    if S_or_SN == 'SN':
                            print(S_or_SN)
                            sendmail_create('A', n)
                            message = request.session["Message"] = "NCR data was succesfully inserted in database and email notification was sent."
                            error_message = ""
                            
                            
                    elif S_or_SN == 'S':
                        message = request.session["Message"] = "NCR data was succesfully inserted in database."
                    
                except DatabaseError: 
                    #db_update_success = False
                    error_message = 'Error occured while inserting new NCR data in database. (NCR#' + ncr_no +')'       
                   
                except SMTPException:                                
                    send_email_success = False
                    error_message = "There was an error sending an email."    


    if error_message not in ('', None) or is_form_valid == False:

        n =  NcrDetailMstr()
        if ncr_no not in [None, '']: 
            hidden_dept_id = form.data.get('hidden_dept_id')
            try:
                n =  NcrDetailMstr.objects.get(ncr_no=ncr_no) 
            except NcrDetailMstr.DoesNotExist:
                error_message = "Record with NCR#" + ncr_no + "does not exist in NCR_DETAIL_MSTR!"                   
        else:
            hidden_dept_id = form.data.get('dept') 
                

        
        set_dropdowns(form, hidden_dept_id)
         
        context = {
            
                   'nc_discoverer_email':nc_discoverer_email,
                   'form': form, 
                   'ncr_no': ncr_no, 
                   'error_message': error_message, 
                   'data' : n, 
                   'nc_conformed_by_name' : nc_conformed_by_name,   
                   'ic_approve_by_name' : ic_approve_by_name,   
                   'rca_approve_by_name' : rca_approve_by_name,
                   'ca_checked_by_sh_name' :ca_checked_by_sh_name,
                   'ra_check_by_sh_name' : ra_check_by_sh_name,
                   'ic_incharge_name' : ic_incharge_name,
                   'rca_incharge_name' : rca_incharge_name, 
                   'ra_check_by_staff_name' : ra_check_by_staff_name, 
                   'ca_approved_by_mgr_name' : ca_approved_by_mgr_name,
                   'se_check_by_mgr_name' : se_check_by_mgr_name,
                   'deny_reasonA' : deny_reasonA, 
                   'deny_reasonB' : deny_reasonB, 
                   'deny_reasonC' : deny_reasonC, 
                   'deny_reasonD' : deny_reasonD, 
                   'deny_reasonE' : deny_reasonE, 
                   'deny_reasonF' : deny_reasonF,
                   'isChecker' : isChecker,
                   'isSH' : isSH,
                   'isGrpMgr' : isGrpMgr,
                   'isAdmin' : isAdmin,
                   'logged_username' : logged_username}  

        # display error on screen
        return render(request, 'NCRMgmntSystem/ncr_create.html', context)      
    
    
    
    else:

        if send_email_success:
            db_transact = db_transact + "E"    
        
        # After the operation was successful, redirect to some other page    
        print('END : ncr_create')
        return redirect('/ncr/ncr_create_view_upd/' + ncr_no + '/' + db_transact) 


def ncr_create_insert(request, form, login_user_chapa_no):
    print('START : ncr_create_insert')
    
    current_datetime = datetime.datetime.now()
    #current_datetime = datetime.datetime.now(tz=timezone.utc)
    
    
    print('current_datetime>> ' + str(current_datetime))
    
    serial_no = '0000'
    deadline = ''




    #get input values from screen
    ncr_no = form.cleaned_data['ncr_no']        
    ncr_issue_date = form.cleaned_data['ncr_issue_date']
    dept = form.cleaned_data['dept']
    project = form.cleaned_data['project']

    source = form.cleaned_data['source']
    other_source = form.cleaned_data['other_source']
    classification = form.cleaned_data['classification']
    nc_detail_description = form.cleaned_data['nc_detail_description']
    nc_discovered_by = form.cleaned_data['nc_discovered_by']
    nc_conformed_by = form.cleaned_data['nc_conformed_by']
    comments = form.cleaned_data['comments']

    ic_incharge = form.cleaned_data['ic_incharge']

    #2024/05/08
    nc_discoverer_email = form.cleaned_data['nc_discoverer_email']
    
    
    if nc_discoverer_email not in ('',None):
        nc_discovered_by = nc_discovered_by +"||"+ nc_discoverer_email
    

    
    #set serial_no
    sqlStmt = "SELECT count(*) FROM seq_table WHERE name = '" + str(dept.id) + "-" + str(project.id) + "'"       

    cnt = 0
    with connection.cursor() as c:
        c.execute(sqlStmt)
        nxt = c.fetchone()
        cnt = nxt[0]

    if cnt == 0:
        try:
            cursor=connection.cursor()
            cursor.execute("INSERT INTO seq_table (name,value) VALUES('" + str(dept.id) + "-" + str(project.id) + "', 0);")    
        except DatabaseError:
            error_message = "Error occured while updating SEQ_TABLE"              
        finally:    
            cursor.close
    
    try:
        cursor=connection.cursor()
        cursor.execute("UPDATE seq_table SET value = LAST_INSERT_ID(value+1) WHERE name = '" + str(dept.id) + "-" + str(project.id) + "';")    
    except DatabaseError:
        error_message = "Error occured while updating SEQ_TABLE"  
    finally:    
        cursor.close
    
    sqlStmt = "SELECT LAST_INSERT_ID();"
    
    with connection.cursor() as c:
        c.execute(sqlStmt)
        nxt = c.fetchone()
        serial_no = nxt[0]
        
    print('serial_no >>>' + str(serial_no))     
        
    #set project_code    
    project_code = '?'    
    try:
        p = Project.objects.get(id=project.id)
        project_code = p.code
    except Project.DoesNotExist:
        error_message = 'Record with id = ' + project.id + ' doesn''t exist in Project table.'
                
    try:
        d = Dept.objects.get(id=dept.id)
        dept_code = d.code
    except Dept.DoesNotExist:
        error_message = 'Record with id = ' + project.id + ' doesn''t exist in Dept table.'
            
    ncr_no = 'NCR-' + str(ncr_issue_date) + '-' + dept_code + '-' + project_code + '-' + (str(serial_no)).zfill(4) 
    
       
    print('ncr_no =' + ncr_no)
        
    #set deadline
    days_in_month = 0
    
    if classification == '1':
        days_in_month = 14
    elif classification == '2': 
        days_in_month = calendar.monthrange(ncr_issue_date.year, ncr_issue_date.month)[1]
                                 
    deadline = ncr_issue_date + timedelta(days=days_in_month)    
    
    print('deadline =' + str(deadline))
    
    print('ncr_issue_date =' + str(ncr_issue_date))
    
    n = NcrDetailMstr()
        
    #set values to database
    n.ncr_no = ncr_no
    n.rev_no = 0
    
    n.ncr_issue_date = ncr_issue_date
    #date_str = str(ncr_issue_date) + ' 14:30:00+0000'
    #date_format = '%Y-%m-%d %H:%M:%S%z'
    #date_obj = datetime.datetime.strptime(date_str, date_format)
    #print('date_obj =' + str(date_obj))
    #n.ncr_issue_date = date_obj
    
    
    n.dept_id =  dept.id
    n.project_id = project.id
    n.source = source
    n.other_source = other_source
    n.classification = classification
    n.nc_detail_description = nc_detail_description
    n.ncr_issue_by = login_user_chapa_no
    n.nc_discovered_by = nc_discovered_by
    n.nc_conformed_by = nc_conformed_by.chapano
    
    n.deadline = deadline
    #date_str = str(deadline) + ' 14:30:00+0000'
    #date_format = '%Y-%m-%d %H:%M:%S%z'
    #date_obj = datetime.datetime.strptime(date_str, date_format)
    #n.deadline = date_obj
    
    n.status = '1'
    
    if ic_incharge not in ('', None):
        n.ic_incharge = str(ic_incharge.chapano)
        
    n.comments = comments
    n.insert_date = current_datetime  
    n.insert_user_id  = login_user_chapa_no
    n.update_date = current_datetime  
    n.update_user_id  = login_user_chapa_no
    
    logged_user_dept_id = ''
    
    if "logged_user_dept_id" in request.session:
        logged_user_dept_id = request.session["logged_user_dept_id"]  
            
    try:
        #insert data
        n.save()
    except DatabaseError as err:
        print ("I got this error: ", err)
        raise 



    print('END : ncr_create_insert')
    return n
    

def ncr_create_update(request, form, ncr_no, login_user_chapa_no, edit_cause):
    print('START : ncr_create_update')
    
    current_datetime = datetime.datetime.now()
    #current_datetime = datetime.datetime.now(tz=timezone.utc)




    source = form.cleaned_data['source']
    other_source = form.cleaned_data['other_source']
    classification = form.cleaned_data['classification']
    nc_detail_description = form.cleaned_data['nc_detail_description']
    nc_discovered_by = form.cleaned_data['nc_discovered_by']
    nc_conformed_by = form.cleaned_data['nc_conformed_by']
    ic_description = form.cleaned_data['ic_description']
    rca_description = form.cleaned_data['rca_description']  
    ca_necessary = form.cleaned_data['ca_necessary'] 
    ca_target_date = form.cleaned_data['ca_target_date'] 
    ca_description = form.cleaned_data['ca_description'] 
    ca_approved_by_mgr = form.cleaned_data['ca_approved_by_mgr'] 
    ra_description = form.cleaned_data['ra_description'] 
    ra_action_effective = form.cleaned_data['ra_action_effective'] 
    ra_followup_date = form.cleaned_data['ra_followup_date']
    se_description = form.cleaned_data['se_description'] 
    se_ro_updated = form.cleaned_data['se_ro_updated']
    se_check_by_qa = form.cleaned_data['se_check_by_qa'] 
    comments = form.cleaned_data['comments']
    ic_approve_by = form.cleaned_data['ic_approve_by']
    rca_approve_by = form.cleaned_data['rca_approve_by']
    ca_checked_by_sh = form.cleaned_data['ca_checked_by_sh']
    ra_check_by_sh = form.cleaned_data['ra_check_by_sh']
    se_check_by_mgr = form.cleaned_data['se_check_by_mgr']
    ic_incharge = form.cleaned_data['ic_incharge']

    
    
    #2024/05/08
    nc_discoverer_email = form.cleaned_data['nc_discoverer_email']
    
    
    if nc_discoverer_email not in ('',None):
        nc_discovered_by = nc_discovered_by +"||"+ nc_discoverer_email


    
   #Start adding for additional request Edric 2024/03/06
    has_desc_F = False
    has_desc_E = False
    has_desc_D = False
    has_desc_C = False
    has_desc_B = False
    has_desc_A = False
    

        
        
    
    if se_description not in ('',None):
        has_desc_F = True
    elif ra_description not in ('',None):
        has_desc_E = True
    elif ca_description not in ('',None):
        has_desc_D = True
    elif rca_description not in ('',None):
        has_desc_C = True
    elif ic_description not in ('',None):
        has_desc_B = True
    elif nc_detail_description not in ('',None):
        has_desc_A = True
        
        
    S_or_SN = form.cleaned_data['S_or_SN'] #save or save and notify
    #End adding for additional request Edric Marinas 2024/03/06



    
    #Start adding For Additional Request Edric Marinas 2024/02/26
    try:
        if se_ro_updated[0] != '1':
            se_ro_updated = '0'
        else:#If se_ro_updated[0] = 1 make it integer type instead of list type
            se_ro_updated = '1'
    except:
        if se_ro_updated !='1':
            se_ro_updated = '0'



    #Start adding for additional Request Edric Marinas 2024/04/04
    hidden_cancel_reason = form.cleaned_data['hidden_cancel_reason'];
    hidden_request_cancel = form.cleaned_data['hidden_request_cancel'];
    
    #End adding for additional Request Edric Marinas 2024/04/04
    

    


    try:
        n =  NcrDetailMstr.objects.get(ncr_no=ncr_no)  

        #A. Nonconformance detail description
        n_source = ''    
        if (n.source not in ('', None)):
            n_source = n.source
        n_other_source = ''    
        if (n.other_source not in ('', None)):
            n_other_source = n.other_source
        n_classification = ''    
        if (n.classification not in ('', None)):
            n_classification = n.classification 
        n_nc_detail_description = ''    
        if (n.nc_detail_description not in ('', None)):
            n_nc_detail_description = n.nc_detail_description
        n_nc_discovered_by = ''    
        if (n.nc_discovered_by not in ('', None)):
            n_nc_discovered_by = n.nc_discovered_by  
        n_nc_conformed_by = ''    
        if (n.nc_conformed_by not in ('', None)):
            n_nc_conformed_by = n.nc_conformed_by      
        nc_conformed_by_chapano = ''
        if nc_conformed_by not in ('', None):
            nc_conformed_by_chapano = nc_conformed_by.chapano   
    
        #B. Immediate Correction     
        n_ic_description = ''    
        if (n.ic_description not in ('', None)):
            n_ic_description = n.ic_description
        n_ic_incharge = ''    
        if (n.ic_incharge not in ('', None)):
            n_ic_incharge = n.ic_incharge
        ic_incharge_chapano = ''
        if ic_incharge not in ('', None):
            ic_incharge_chapano = ic_incharge.chapano
        n_ic_approve_by = ''    
        if (n.ic_approve_by not in ('', None)):
            n_ic_approve_by = n.ic_approve_by
        ic_approve_by_chapano = ''
        if ic_approve_by not in ('', None):
            ic_approve_by_chapano = ic_approve_by.chapano     

        #C. Root Cause Analysis(5 Whys, Fishbone, etc)    
        n_rca_description = ''    
        if (n.rca_description not in ('', None)):
            n_rca_description = n.rca_description
        n_ca_necessary = ''    
        if (n.ca_necessary not in ('', None)):
            n_ca_necessary = n.ca_necessary 
        n_rca_approve_by = ''    
        if (n.rca_approve_by not in ('', None)):
            n_rca_approve_by = n.rca_approve_by 
        rca_approve_by_chapano = ''
        if rca_approve_by not in ('', None):
            rca_approve_by_chapano = rca_approve_by.chapano    

        #D. Corrective Action to the cause
        n_ca_description = ''    
        if (n.ca_description not in ('', None)):
            n_ca_description = n.ca_description
        n_ca_target_date = ''    
        if (n.ca_target_date not in ('', None)):
            n_ca_target_date = n.ca_target_date  
        ca_target_date_str = ''    
        if (ca_target_date not in ('', None)):
            ca_target_date_str = ca_target_date  
        n_ca_approved_by_mgr = ''    
        if (n.ca_approved_by_mgr not in ('', None)):
            n_ca_approved_by_mgr = n.ca_approved_by_mgr      
        ca_approved_by_mgr_chapano = ''
        if ca_approved_by_mgr not in ('', None):
            ca_approved_by_mgr_chapano = ca_approved_by_mgr.chapano
        n_ca_checked_by_sh = ''    
        if (n.ca_checked_by_sh not in ('', None)):
            n_ca_checked_by_sh = n.ca_checked_by_sh  
        ca_checked_by_sh_chapano = ''
        if ca_checked_by_sh not in ('', None):
            ca_checked_by_sh_chapano = ca_checked_by_sh.chapano
    
        #E. Result of action 
        n_ra_description = ''    
        if (n.ra_description not in ('', None)):
            n_ra_description = n.ra_description
        n_ra_action_effective = ''    
        if (n.ra_action_effective not in ('', None)):
            n_ra_action_effective = n.ra_action_effective  
        n_ra_followup_date = ''    
        if (n.ra_followup_date not in ('', None)):
            n_ra_followup_date = n.ra_followup_date  
        ra_followup_date_str = ''    
        if (ra_followup_date not in ('', None)):
            ra_followup_date_str = ra_followup_date      
    
        #F. Show Effectiveness  
        n_se_description = ''    
        if (n.se_description not in ('', None)):
            n_se_description = n.se_description
        n_se_ro_updated = ''    
        if (n.se_ro_updated not in ('', None)):
            n_se_ro_updated = n.se_ro_updated  
        n_se_check_by_qa = ''    
        if (n.se_check_by_qa not in ('', None)):
            n_se_check_by_qa = n.se_check_by_qa     
        se_check_by_qa_chapano = ''
        if se_check_by_qa not in ('', None):
            se_check_by_qa_chapano = se_check_by_qa.chapano
        
        n_ra_check_by_sh = ''    
        if (n.ra_check_by_sh not in ('', None)):
            n_ra_check_by_sh = n.ra_check_by_sh
        ra_check_by_sh_chapano = ''
        if ra_check_by_sh not in ('', None):
            ra_check_by_sh_chapano = ra_check_by_sh.chapano
        
        n_se_check_by_mgr = ''    
        if (n.se_check_by_mgr not in ('', None)):
            n_se_check_by_mgr = n.se_check_by_mgr 
        se_check_by_mgr_chapano = ''
        if se_check_by_mgr not in ('', None):
            se_check_by_mgr_chapano = se_check_by_mgr.chapano
    
        if edit_cause != '0':
            n.rev_no = n.rev_no + 1



        has_change_A = False
        has_change_B = False
        has_change_C = False
        has_change_D = False
        has_change_E = False
        has_change_F = False
        
        #Edric Marinas 2024/04/04
        if hidden_request_cancel != '7':
        
            
            #A. Nonconformance detail description
            if (n_source != source or n.other_source != n_other_source or n_classification != classification or n_nc_detail_description != nc_detail_description or n_nc_discovered_by != nc_discovered_by or n_nc_conformed_by != nc_conformed_by.chapano or n_ic_incharge != ic_incharge_chapano) and ic_description in ('', None):        
                has_change_A = True  
    
                n.source = source
                n.other_source = other_source
                n.classification = classification
                n.nc_detail_description = nc_detail_description 
                n.nc_discovered_by = nc_discovered_by
                n.nc_conformed_by = nc_conformed_by.chapano
    
                n.ic_incharge = ic_incharge_chapano
    
                days_in_month = 0
                issue_date = n.ncr_issue_date
    
                if n.classification == '1':
                    days_in_month = 14
                elif n.classification == '2': 
                    days_in_month = calendar.monthrange(issue_date.year, issue_date.month)[1]
    
                n.deadline = issue_date + timedelta(days=days_in_month)    
    
                if n.ncr_issue_by in [None, '']:   
                    n.ncr_issue_by = login_user_chapa_no
    
                if edit_cause != '0':
                    n.nc_conformed_date = None
                    n.nc_conforme_status = None
    
            #B. Immediate Correction
            if (n_ic_description != ic_description or n_ic_approve_by != ic_approve_by_chapano) and ic_description not in ('', None):             
                has_change_B = True 
                n.ic_description = ic_description
                #n.ic_incharge = ic_incharge_chapano
                #n.ic_incharge = login_user_chapa_no
    
                if ic_description not in [None, '']:    
                    n.ic_create_date = current_datetime
    
                n.ic_approve_by = ic_approve_by_chapano
                n.status = '4'
                if edit_cause != '0':
                    n.ic_approve_date = None
                    n.ic_approve_status = None
    
            #C. Root Cause Analysis(5 Whys, Fishbone, etc)
            if n_rca_description != rca_description or n_ca_necessary != ca_necessary or n_rca_approve_by != rca_approve_by_chapano:                
                has_change_C = True  
    
                n.rca_description = rca_description 
                
                n.rca_create_date  = current_datetime        
    
                #n.ca_necessary = ca_necessary
                if n.classification == '2':
                    n.ca_necessary = '1'
                else:    
                    n.ca_necessary = ca_necessary
    
                if n.rca_incharge in ('', None):
                    n.rca_incharge = login_user_chapa_no
                n.rca_approve_by = rca_approve_by_chapano
                
                if edit_cause != '0':
                    n.rca_approve_date = None
                    n.rca_approve_status = None
    
                    n.ca_check_date_by_sh = None
                    n.ca_check_by_sh_status = None
                    n.ca_approved_date_by_mgr = None
                    n.ca_approve_by_mgr_status = None
    
            #D. Corrective Action to the cause
            if n_ca_description != ca_description or n_ca_target_date != ca_target_date_str or n_ca_approved_by_mgr != ca_approved_by_mgr_chapano or n_ca_checked_by_sh != ca_checked_by_sh_chapano:            
                has_change_D = True  
    
                n.ca_description = ca_description 
                #n.ca_create_by = rca_incharge_chapano 
                n.ca_create_by = login_user_chapa_no
                n.ca_create_date  = current_datetime        
                n.ca_target_date = ca_target_date
                n.ca_checked_by_sh = ca_checked_by_sh_chapano
                n.ca_approved_by_mgr = ca_approved_by_mgr_chapano
    
                if edit_cause != '0':
                    n.ca_check_date_by_sh = None
                    n.ca_check_by_sh_status = None
                    n.ca_approved_date_by_mgr = None
                    n.ca_approve_by_mgr_status = None
    
                    if n.rca_approve_status != '1': 
                        n.rca_approve_date = None
                        n.rca_approve_status = None
    
                if ca_description in ('', None):    
                    n.ca_target_date = None
                    n.ca_create_by = None
                    n.ca_create_date = None
                    n.ca_checked_by_sh = None
                    n.ca_check_date_by_sh = None
                    n.ca_check_by_sh_status = None
                    n.ca_approved_by_mgr = None
                    n.ca_approved_date_by_mgr = None
                    n.ca_approve_by_mgr_status = None
    
            #if return-To-C and D. has no inputs         
            if edit_cause == '2' and ca_description in ('', None):
                n.ca_checked_by_sh = None
                n.ca_approved_by_mgr = None
    
            #E. Result of action           
            if n_ra_description != ra_description or n_ra_action_effective != ra_action_effective or n_ra_followup_date != ra_followup_date_str or n_ra_check_by_sh != ra_check_by_sh_chapano or n_se_check_by_mgr != se_check_by_mgr_chapano or n_se_check_by_qa != se_check_by_qa_chapano:        
                has_change_E = True  
    
                n.ra_description = ra_description 
                n.ra_action_effective = ra_action_effective 
                n.ra_followup_date = ra_followup_date
                if n.ra_check_by_staff in ('', None):
                    n.ra_check_by_staff = login_user_chapa_no
    
                n.ra_check_date_by_staff = current_datetime
                n.ra_check_by_staff_status = '1'
    
                n.ra_check_by_sh = ra_check_by_sh_chapano
                n.se_check_by_mgr = se_check_by_mgr_chapano 
                n.se_check_by_qa = se_check_by_qa_chapano
    
                if edit_cause != '0':
                    n.ra_check_date_by_sh = None
                    n.ra_check_by_sh_status = None    
                    n.se_check_date_by_mgr = None
                    n.se_check_by_mgr_status = None
                    n.se_check_date_by_qa = None
                    n.se_check_by_qa_status = None
    
                if ra_description in ('', None): 
                    n.ra_action_effective = None
                    n.ra_followup_date = None
                    n.ra_check_by_staff = None
                    n.ra_check_by_staff_status = None
                    n.ra_check_date_by_staff = None
                    n.ra_check_by_sh = None
                    n.ra_check_date_by_sh = None
                    n.ra_check_by_sh_status = None
    
                    n.se_check_by_mgr = None
                    n.se_check_date_by_mgr = None 
                    n.se_check_by_mgr_status = None
                    n.se_check_by_qa = None
                    n.se_check_date_by_qa = None
                    n.se_check_by_qa_status = None
    
            #F. Show Effectiveness  
            if n_se_description != se_description:     
                has_change_F = True  
                n.se_description = se_description 
               
                if edit_cause != '0':
                    n.ra_check_date_by_sh = None
                    n.ra_check_by_sh_status = None    
                    n.se_check_date_by_mgr = None
                    n.se_check_by_mgr_status = None    
                    n.se_check_date_by_qa = None
                    n.se_check_by_qa_status = None                            
    
                if se_description in ('', None):  
                    n.se_ro_updated = None 
            
            

        
        
        
        n.se_ro_updated = se_ro_updated       
        n.comments = comments    
        n.update_user_id = login_user_chapa_no
        n.update_date = current_datetime
        #Start modifying for additional request Edric Marinas 2024/04/17
        try:
            has_update = False

            if has_change_A or has_change_B or has_change_C or has_change_D or has_change_E or has_change_F:
                has_update = True
            
                
            #update data
            
            n.save()
            request.session["Message"] = 'NCR data was succesfully updated in database and email notification was sent.'
            #S = save SN = Save and notify
            if S_or_SN == 'SN':
                #send email notification
                if edit_cause == '2' not in ('', None):
                    sendmail_create('E-returnToC', n)

                elif has_change_A:
                    sendmail_create('A', n)

                elif has_change_B:   
                    sendmail_create('B', n)

                elif has_change_C and has_change_D:
                    sendmail_create('C&D', n) 

                elif has_change_C and n.ca_necessary == '1':
                    sendmail_create('C-Yes', n)

                elif has_change_C and n.ca_necessary == '0':    
                    sendmail_create('C-No', n)

                elif has_change_D:    
                    sendmail_create('D', n)

                elif n.classification == '2' and n.se_description not in ('', None):  
                    if has_change_E and has_change_F:
                        sendmail_create('E-proceedToF', n)

                    elif has_change_E:
                        sendmail_create('E', n)

                    elif has_change_F:    
                        sendmail_create('F', n)

                    elif classification == '1' and ra_description not in ('', None):
                        sendmail_create('E', n)
                      
                        
                #Start adding for additional request Edric 2024/03/06
                else:
                    request.session["Message"] = 'Email notification was sent.'
                    if n.classification == '2' and n.se_description not in ('', None):
                        
                        if classification == '1' and ra_description not in ('', None):
                            sendmail_create('E', n)

                            
                        elif has_desc_F:
                            sendmail_create('F', n)

                            
                        elif has_desc_E:
                            sendmail_create('E', n)

                            
                        elif has_desc_E and has_desc_F:
                            sendmail_create('E-proceedToF', n)
                            
                        

                        
                    elif has_desc_D:
                        sendmail_create('C_approved-y/n', n)

                        
                    elif has_desc_C and n.ca_necessary == '0':    
                        sendmail_create('C-No', n)

                    
                    elif has_desc_C and n.ca_necessary == '1':
                        sendmail_create('C-Yes', n)

                        
                        
                    elif has_desc_B:
                        sendmail_create('B', n)

                    
                    elif has_desc_A:
                        sendmail_create('A', n)

                    
                    else:
                        print(">>>>>>>>>>ERROR")
            
            #Cancel request 2024/04/04
            elif hidden_request_cancel == '7':
                request.session["Message"] = ''
                phase = str(declarePhase(ncr_no))
                try:
                    cursor=connection.cursor()
                    if cursor.execute("UPDATE deny_reason SET accepted_date = SYSDATE(),reason = '"+hidden_cancel_reason+"',denied_by = '',rev_no = '"+phase+"',phase = 'G' WHERE ncr_no = '" + n.ncr_no + "' AND phase='H' "):
                        request.session["Message"] = "Request to cancel is success"
                    else:
                        try:
                            create_cancel_request(n.ncr_no, phase , 'G', hidden_cancel_reason, request.session["logged_user_chapa_no"], current_datetime)
                            request.session["Message"] = "Request to cancel is success"
                        except:
                            error_message = 'Error occured while inserting NCR data in database. (NCR#' + ncr_no +')' 
                except DatabaseError:
                    error_message = 'Error occured while inserting NCR data in database. (NCR#' + ncr_no +')'                           
                finally:    
                    cursor.close
                   
                    if request.session["Message"] not in (''):
                        n.status = '7'
                        n.save()
                        sendmail_NCR_cancel_request(phase, n)
                    else:
                       error_message = 'Error occured while inserting NCR data in database. (NCR#' + ncr_no +')' 
                       
                
            elif has_update:
                n.save()
                request.session["Message"] = "NCR data was succesfully updated in database" 
            else:
                request.session["Message"] = "No change was made"         
            #End adding for additional request Edric 2024/03/06
            
                    
        except SMTPException:                   
            raise
        except DatabaseError:
            raise             
    except NcrDetailMstr.DoesNotExist:
        raise
    
    print('END : ncr_create_update')
    return n


def get_latest_update_date(request):
    ncr_no = request.GET.get('ncr_no')
    hidden_update_date = request.GET.get('hidden_update_date')
    isLatest = 'TRUE' 
    latest_update_date = ''
    latest_update_by = ''
    
    try:
        n =  NcrDetailMstr.objects.get(ncr_no=ncr_no)   
        latest_update_date = str(n.update_date)
        
        if str(hidden_update_date) != latest_update_date:
            isLatest = 'FALSE'   
            try:
                e = Employee.objects.get(chapano=n.update_user_id)
                latest_update_by = e.lastname + ', ' + e.firstname + e.middlename
            except Employee.DoesNotExist:
                latest_update_by = 'Unknown'          
        
    except NcrDetailMstr.DoesNotExist:
        error_message = 'Record with ncr_no = ' + ncr_no + ' doesn''t exist in NcrDetailMstr table.'
    
    data = {
        'isLatest': isLatest, 'latest_update_date':latest_update_date, 'latest_update_by': latest_update_by,
    }    
    
    return JsonResponse(data)


def employee_password_change_view(request, chapano): 
    print('START: employee_password_change_view')
    
    success_message = ''
    error_message = ''
    
    if "logged_user_chapa_no" in request.session:
        logged_user_chapa_no = request.session["logged_user_chapa_no"] 
        
        if "logged_username" in request.session:
            logged_username = request.session["logged_username"]         
            
        if "isChecker" in request.session:    
            isChecker = request.session["isChecker"] 
            
        if "isSH" in request.session:    
            isSH = request.session["isSH"]
            
        if "isGrpMgr" in request.session:    
            isGrpMgr = request.session["isGrpMgr"]
            
        if "isAdmin" in request.session:    
            isAdmin = request.session["isAdmin"]  
        
        try:
            e = Employee.objects.get(chapano=chapano)            
        
        except Employee.DoesNotExist:
            error_message = "Record with chapano = " + chapano + "does not exist in Employee table."
            pass        
        
        form = EmployeePasswordForm(initial={
                    'chapano' : e.chapano,   
                    'name' : e.lastname + ", " + e.firstname + " " + e.middlename + ".",
                    'currentPassword' : '', 
                    'newPassword' : '', 
                    'confirmPassword' : '', 
                    })
        
        context = {'form': form, 
                   'success_message' : success_message , 
                   'error_message': error_message,
                   'logged_username': logged_username,
                   'isChecker': isChecker,
                   'isSH': isSH,
                   'isGrpMgr': isGrpMgr,
                   'isAdmin': isAdmin,
                   'data': e,
                   'logged_user_chapa_no': logged_user_chapa_no,
                   }   
        
        print('END: employee_password_change_view')
        return render(request,'NCRMgmntSystem/employee_password_change.html', context)  

    else:        
        print('END: employee_password_change_view')
        return redirect('/ncr/logout')     
    
    
def employee_password_change(request, chapano): 
    print('START: employee_password_change')
    
    success_message = ''
    error_message = ''
    
    if "logged_user_chapa_no" in request.session:
        logged_user_chapa_no = request.session["logged_user_chapa_no"] 
        
        if "logged_username" in request.session:
            logged_username = request.session["logged_username"]         
            
        if "isChecker" in request.session:    
            isChecker = request.session["isChecker"] 
            
        if "isSH" in request.session:    
            isSH = request.session["isSH"]
            
        if "isGrpMgr" in request.session:    
            isGrpMgr = request.session["isGrpMgr"]
            
        if "isAdmin" in request.session:    
            isAdmin = request.session["isAdmin"]         
        
        if request.method == "POST":  
            form = EmployeePasswordForm(request.POST)  
            
            if form.is_valid():  
                currentPassword = form.cleaned_data['currentPassword']
                newPassword = form.cleaned_data['newPassword'] 
                confirmPassword = form.cleaned_data['confirmPassword']
            
                try:  
                    e = Employee.objects.get(chapano=chapano) 
                        
                    if currentPassword != e.password:
                        error_message = 'Current password is incorrect.'
                        
                    elif newPassword != confirmPassword:    
                        error_message = 'New password and Confirm password does not match.'
                        
                    else:
                        e.password = newPassword
                        e.save()  
                        success_message = 'Data successfully updated in database.'
                
                except:      
                    error_message = 'Data not found.'
                    pass    

            context = {'form': form, 
               'success_message' : success_message , 
               'error_message': error_message,
               'logged_username': logged_username,
               'isChecker': isChecker,
               'isSH': isSH,
               'isGrpMgr': isGrpMgr,
               'isAdmin': isAdmin,
               'data': e,
               'logged_user_chapa_no': logged_user_chapa_no,
               }  
            print('END: employee_password_change')
            return render(request,'NCRMgmntSystem/employee_password_change.html', context)     

    
    else:        
        print('END: employee_password_change')
        return redirect('/ncr/logout') 

#Start added Edric Marinas 2024/04/11
def declarePhase(ncr_no):

    phase = ''
    """
    has_date_A = False
    has_date_B = False
    has_date_C = False
    has_date_d = False
    has_date_D = False
    has_date_E = False
    has_date_f = False
    has_date_F = False
    
    

        phase    

    """  

    try:
        n =  NcrDetailMstr.objects.get(ncr_no=ncr_no)      
        if n.se_check_date_by_qa not in ('',None):
            phase = '8'
        elif n.se_check_date_by_mgr not in ('',None):
            phase = '7'
        elif n.ra_check_date_by_sh not in ('',None):
            phase = '6'
        elif n.ca_approved_date_by_mgr not in ('',None):
            phase = '5'
        elif n.ca_check_date_by_sh not in ('',None):
            phase = '4'
        elif n.rca_approve_date not in ('',None):
            phase = '3'
        elif n.ic_approve_date not in ('',None):
            phase = '2'
        elif n.nc_conformed_by not in ('',None):
            phase = '1'
    except:
        print("Declare Phase Error")

    return phase


def sendmail_ncr_cancelled(n,logged_chapaNo):
    subject = 'NCR Create Status Notification: ' + str(n.ncr_no)       
    from_email = 'NCR_Mgnt_Sys@shi-g.com'
    send_to = ""


    try:
        e =  Employee.objects.get(chapano=n.ca_checked_by_sh)
        if n.ca_checked_by_sh != logged_chapaNo:
            e =  Employee.objects.get(chapano=n.ca_checked_by_sh)
            send_to = e.email
            user_id = e.chapano
            content = "Sir/Madam,\n\n    A Nonconformance has been cancelled in your section. \n\n    " + PROJ_URL + "ncr_verify_view_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply. "
            send_mail(subject, content, from_email, [send_to], fail_silently=False,)
    except:
        print("No ca_checked_by_sh")


    try:#send mail to Incharge
        e = Employee.objects.get(chapano=n.ic_incharge)
        send_to = e.email
        user_id = e.chapano
        content = "Sir/Madam,\n\n    A Nonconformance has been cancelled in your section. \n\n    " + PROJ_URL + "ncr_create_view_upd_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply. "
        send_mail(subject, content, from_email, [send_to], fail_silently=False,)
    except:
        print("no ic_incharge")

    
    try: #send mail to RCA approve by OR ca Checked by if ever they are not the same user (BOTH WILL RECEIVE IF THE ONE WHO CANCEL NCR IS NEITHER ONE OF THEM)
        e =  Employee.objects.get(chapano=n.rca_approve_by)    
        if n.rca_approve_by not in  (n.ca_checked_by_sh,logged_chapaNo):#check if the user logged in is not same as SH
            e =  Employee.objects.get(chapano=n.rca_approve_by)
            send_to = e.email
            user_id = e.chapano
            content = "Sir/Madam,\n\n    A Nonconformance has been cancelled in your section. \n\n    " + PROJ_URL + "ncr_verify_view_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply. "
            send_mail(subject, content, from_email, [send_to], fail_silently=False,)
        else:
            print("rca_approve_by and ca_checked_by_sh are same person or logged user is same as rca_approve_by")
    except:
        print("no rca_approve_by ")

    
    try:
        e = Employee.objects.get(chapano=n.ca_approved_by_mgr)
        send_to = e.email
        user_id = e.chapano
        if logged_chapaNo != user_id:
            content = "Sir/Madam,\n\n    A Nonconformance has been cancelled in your section. \n\n    " + PROJ_URL + "ncr_verify_view_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply. "
            send_mail(subject, content, from_email, [send_to], fail_silently=False,)
    except:
        print("No ca_approved_by_mgr")

    
    try:
        e = Employee.objects.get(chapano=n.se_check_by_mgr)
        send_to = e.email
        user_id = e.chapano
        if logged_chapaNo != user_id:
            content = "Sir/Madam,\n\n    A Nonconformance has been cancelled in your section. \n\n    " + PROJ_URL + "ncr_verify_view_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply. "
            send_mail(subject, content, from_email, [send_to], fail_silently=False,)
    except:
        print("No se_check_by_mgr")
    
    
    try:
        e = Employee.objects.get(chapano=n.se_check_by_qa)
        send_to = e.email
        user_id = e.chapano
        if logged_chapaNo != user_id:
            content = "Sir/Madam,\n\n    A Nonconformance has been cancelled in your section. \n\n    " + PROJ_URL + "ncr_verify_view_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply. "
            send_mail(subject, content, from_email, [send_to], fail_silently=False,)
    except:
        print("No se_check_by_qa")

    return


def sendmail_NCR_cancel_request(mailType, n):
    subject = 'NCR Create Status Notification: ' + str(n.ncr_no)       
    from_email = 'NCR_Mgnt_Sys@shi-g.com'
    send_to = ''  
    
    
    if mailType == '0':

        
        #d = DenyReason.objects.get(ncr_no=n.ncr_no,)

        e =  Employee.objects.get(chapano=n.ic_incharge)
        send_to = e.email
        user_id = e.chapano
        content = "Sir/Madam,\n\n    A Nonconformance you request for cancellation is denied. \n\n    " + PROJ_URL + "ncr_create_view_upd_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply. "+mailType+"  "
        send_mail(subject, content, from_email, [send_to, ], fail_silently=False,)
        return
    
    
    elif mailType == '1':
        e =  Employee.objects.get(chapano=n.nc_conformed_by)
        send_to = e.email
        user_id = e.chapano
        

    elif mailType == '2':
        e =  Employee.objects.get(chapano=n.ic_approve_by)
        send_to = e.email
        user_id = e.chapano
        
    
    elif mailType == '3':
        e =  Employee.objects.get(chapano=n.rca_approve_by)
        send_to = e.email
        user_id = e.chapano
        


    elif mailType == '4':
        e =  Employee.objects.get(chapano=n.ca_checked_by_sh)
        send_to = e.email
        user_id = e.chapano
        
    elif mailType == '5':
        
        try:
            e =  Employee.objects.get(chapano=n.ca_checked_by_sh)
            send_to = e.email
            user_id = e.chapano
            content = "Sir/Madam,\n\n    A Nonconformance has been requested to be cancelled in your section. \n\n    " + PROJ_URL + "ncr_verify_view_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply. "
            send_mail(subject, content, from_email, [send_to, ], fail_silently=False,)
        except DatabaseError:
            print("There was an error sending an email to ca_checked_by_sh.")
        
        try:
            e =  Employee.objects.get(chapano=n.ca_approved_by_mgr)
            send_to = e.email
            user_id = e.chapano
            content = "Sir/Madam,\n\n    A Nonconformance has been requested to be cancelled in your section. \n\n    " + PROJ_URL + "ncr_verify_view_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply. "
            send_mail(subject, content, from_email, [send_to, ], fail_silently=False,)
        except DatabaseError:
            print("There was an error sending an email to ca_approved_by_mgr.")
        
        return

    elif mailType == '6':
        e =  Employee.objects.get(chapano=n.ra_check_by_sh)
        send_to = e.email
        user_id = e.chapano
   

    #elif mailType == 'F':
        #e =  Employee.objects.get(chapano=n.se_check_by_qa)  
        #send_to = e.email
        #user_id = e.chapano
    elif mailType == '7':

        try:
            e =  Employee.objects.get(chapano=n.ra_check_by_sh)  
            user_id = e.chapano
            send_to = e.email
            content = "Sir/Madam,\n\n    A Nonconformance has been requested to be cancelled in your section. \n\n    " + PROJ_URL + "ncr_verify_view_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply. "
            send_mail(subject, content, from_email, [send_to, ], fail_silently=False,)
        except DatabaseError:
            print("There was an error sending an email to ra_check_by_sh.")


        try :
            e =  Employee.objects.get(chapano=n.se_check_by_qa)
            send_to = e.email
            user_id = e.chapano
            content = "Sir/Madam,\n\n    A Nonconformance has been requested to be cancelled in your section. \n\n    " + PROJ_URL + "ncr_verify_view_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply. "
            send_mail(subject, content, from_email, [send_to, ], fail_silently=False,)
        except DatabaseError:
            print("There was an error sending an email to se_check_by_qa.")


        return
    else:
        print("There was an error sending an email.")



    content = "Sir/Madam,\n\n    A Nonconformance has been requested to be cancelled in your section. \n\n    " + PROJ_URL + "ncr_verify_view_via_mail/" + n.ncr_no + "/" + user_id + "\n\n    Thank you for using the NCR Management System. \n\n    This is a system-generated e-mail. Please do not reply. "+mailType+"  "


    #send email
    try:
        for x in send_to:
            send_mail(subject, content, from_email, [x], fail_silently=False,)

    except:
        send_mail(subject, content, from_email, [send_to, ], fail_silently=False,)

    return


def create_cancel_request(ncr_no, step, phase, reason, corrected_by, corrected_date):
    error_message = ""

    try:
        cursor=connection.cursor()      
        cursor.execute("INSERT INTO deny_reason(ncr_no, rev_no, phase, reason, corrected_by, corrected_date) VALUES('" + ncr_no + "', '" + step + "', '" + phase + "', '" + str(reason) + "', '" + corrected_by + "', '" + str(corrected_date) +  "')")    

    except IntegrityError as e:
        print(e)
        #cursor.execute("UPDATE deny_reason SET corrected_by = '" + corrected_by + "', corrected_date = SYSDATE(), reason = '" + str(reason) + "', accepted_date = null WHERE ncr_no = '" + ncr_no + "' AND phase = '" + step + "'")                    
    except DatabaseError as e:
        print(e)
        error_message = "Error occured while inserting DENY_REASON data in database."   
                        
    finally:    
        cursor.close

    return error_message




#Start Adding Edric Marinas 2024/04/17 
def check_project_NCR(request):      


    id = request.GET.get('id')
    sectionCode = request.GET.get('sectionCode')
    projectCode = request.GET.get('projectCode')

    try:
        has_ncr = NcrDetailMstr.objects.filter(project_id=id).count()
        test = NcrDetailMstr.objects.filter(project_id=id)
        

    except:
        has_ncr = 0

    context = {
        'id':id,
        'sectionCode':sectionCode,
        'projectCode':projectCode,
        'has_ncr':has_ncr,
        'test':test
               }

    return render(request,'NCRMgmntSystem/ajax_check_project_NCR.html',context)
#End Adding Edric Marinas 2024/04/17 

#Start Adding 05/01/2024
def ncr_create_view_history(request, ncr_no, rev_no,pageType):
    print('START : ncr_create_view_history')
    

    template_name = 'NCRMgmntSystem/ncr_create_history.html'
    n = None
    
    nc_conformed_by_name = ''    
    ic_approve_by_name = ''   
    rca_approve_by_name = ''

    ca_checked_by_sh_name = '' 
    ra_check_by_sh_name = ''            
    ic_incharge_name = ''
    rca_incharge_name = ''
    ra_check_by_staff_name = ''
    ca_approved_by_mgr_name = ''
    se_check_by_mgr_name = ''
    se_check_by_qa_name = ''
          



    
    deny_reasonA = ''
    deny_reasonB = ''
    deny_reasonC = ''
    deny_reasonD = ''
    deny_reasonE = ''
    deny_reasonF = ''
    
    is_denied_A = '0' 
    is_denied_B = '0' 
    is_denied_C = '0' 
    is_denied_D = '0' 
    is_denied_E = '0' 
    is_denied_F = '0' 
    
    logged_user_chapa_no = ''
    logged_username = ''
    isChecker = False
    isSH = False
    isGrpMgr = False
    isAdmin = False
    
    
    if "logged_user_chapa_no" in request.session:
        logged = True
        logged_user_chapa_no = request.session["logged_user_chapa_no"] 
                
        if "logged_username" in request.session:
            logged_username = request.session["logged_username"]         
            
        if "isChecker" in request.session:    
            isChecker = request.session["isChecker"] 
            
        if "isSH" in request.session:    
            isSH = request.session["isSH"]
            
        if "isGrpMgr" in request.session:    
            isGrpMgr = request.session["isGrpMgr"]
            
        if "isAdmin" in request.session:    
            isAdmin = request.session["isAdmin"]    
    else:
        logged = False
    
    
    try:

        n =  NcrDetailMstr.objects.get(ncr_no=ncr_no)
        max_rev = n.rev_no
        
        
        sqlStmt = """
                  SELECT * FROM `ncr_detail_mstr_history` WHERE ncr_no = '"""+n.ncr_no+"""' AND rev_no = '"""+ rev_no +"""'  """  
        
        with connection.cursor() as c:
            c.execute(sqlStmt)
            x = namedtuplefetchall(c)
            for n in x:
                print(n.ncr_no)
                
            
    except:
        print("Error")
                    

        
    ncr_issue_date = n.ncr_issue_date
    nc_conformed_date = n.nc_conformed_date
    ic_create_date = n.ic_create_date
    ic_approve_date = n.ic_approve_date
    rca_create_date = n.rca_create_date
    rca_approve_date = n.rca_approve_date
    ca_create_date = n.ca_create_date
    ca_check_date_by_sh = n.ca_check_date_by_sh
    ca_approved_date_by_mgr = n.ca_approved_date_by_mgr 
    ra_check_date_by_staff = n.ra_check_date_by_staff
    ra_check_date_by_sh = n.ra_check_date_by_sh
    se_check_date_by_mgr = n.se_check_date_by_mgr
    se_check_date_by_qa = n.se_check_date_by_qa
            
    if ncr_issue_date not in [None, '']:
        ncr_issue_date = ncr_issue_date.date
    if nc_conformed_date not in [None, '']:
        nc_conformed_date = nc_conformed_date.date
    if ic_create_date not in [None, '']:
        ic_create_date = ic_create_date.date
    if ic_approve_date not in [None, '']:
        ic_approve_date = ic_approve_date.date      
    if rca_create_date not in [None, '']:
        rca_create_date = rca_create_date.date
    if rca_approve_date not in [None, '']:
        rca_approve_date = rca_approve_date.date    
    if ca_create_date not in [None, '']:
        ca_create_date = ca_create_date.date     
    if ca_check_date_by_sh not in [None, '']:
        ca_check_date_by_sh = ca_check_date_by_sh.date
    if ca_approved_date_by_mgr not in [None, '']:
        ca_approved_date_by_mgr = ca_approved_date_by_mgr.date                 
    if ra_check_date_by_staff not in [None, '']:
        ra_check_date_by_staff = ra_check_date_by_staff.date
    if ra_check_date_by_sh not in [None, '']:
        ra_check_date_by_sh = ra_check_date_by_sh.date
    if se_check_date_by_mgr not in [None, '']:
        se_check_date_by_mgr = se_check_date_by_mgr.date
    if se_check_date_by_qa not in [None, '']:
        se_check_date_by_qa = se_check_date_by_qa.date
    
    if n.nc_conformed_by not in [None, '']:
        try:
            e = Employee.objects.get(chapano=n.nc_conformed_by)
            nc_conformed_by_name = e.lastname + ', ' + e.firstname + ' ' + e.middlename
        except Employee.DoesNotExist:
            nc_conformed_by_name = 'unknown'  
        
    if n.ic_incharge not in [None, '']:
        try:
            e = Employee.objects.get(chapano=n.ic_incharge)
            ic_incharge_name = e.lastname + ', ' + e.firstname + ' ' + e.middlename
        except Employee.DoesNotExist:
            ic_incharge_name = 'unknown'  
        
    if n.ic_approve_by not in [None, '']:
        try:
            e = Employee.objects.get(chapano=n.ic_approve_by)
            ic_approve_by_name = e.lastname + ', ' + e.firstname + ' ' + e.middlename
        except Employee.DoesNotExist:
            ic_approve_by_name = 'unknown'   
        
    if n.rca_incharge not in [None, '']:
        try:
            e = Employee.objects.get(chapano=n.rca_incharge)
            rca_incharge_name = e.lastname + ', ' + e.firstname + ' ' + e.middlename
        except Employee.DoesNotExist:
            rca_incharge_name = 'unknown'                        
        
    if n.rca_approve_by not in [None, '']:
        try:
            e = Employee.objects.get(chapano=n.rca_approve_by)
            rca_approve_by_name = e.lastname + ', ' + e.firstname + ' ' + e.middlename
        except Employee.DoesNotExist:
            rca_approve_by_name = 'unknown'
    
    if n.ca_checked_by_sh not in [None, '']:
        try:
            e = Employee.objects.get(chapano=n.ca_checked_by_sh)
            ca_checked_by_sh_name = e.lastname + ', ' + e.firstname + ' ' + e.middlename
        except Employee.DoesNotExist:
            ca_checked_by_sh_name = 'unknown'      
        
    if n.ca_approved_by_mgr not in [None, '']:
        try:
            e = Employee.objects.get(chapano=n.ca_approved_by_mgr)
            ca_approved_by_mgr_name = e.lastname + ', ' + e.firstname + ' ' + e.middlename
        except Employee.DoesNotExist:
            ca_approved_by_mgr_name = 'unknown'  
            
    if n.ra_check_by_staff not in [None, '']:
        try:
            e = Employee.objects.get(chapano=n.ra_check_by_staff)
            ra_check_by_staff_name = e.lastname + ', ' + e.firstname + ' ' + e.middlename
        except Employee.DoesNotExist:
            ra_check_by_staff_name = 'unknown'  
             
    if n.ra_check_by_sh not in [None, '']:
        try:
            e = Employee.objects.get(chapano=n.ra_check_by_sh)
            ra_check_by_sh_name = e.lastname + ', ' + e.firstname + ' ' + e.middlename
        except Employee.DoesNotExist:
            ra_check_by_sh_name = 'unknown' 
    
    if n.se_check_by_mgr not in [None, '']:
        try:
            e = Employee.objects.get(chapano=n.se_check_by_mgr)
            se_check_by_mgr_name = e.lastname + ', ' + e.firstname + ' ' + e.middlename
        except Employee.DoesNotExist:
            se_check_by_mgr_name = 'unknown'
    
    if n.se_check_by_qa not in [None, '']:
        try:
            e = Employee.objects.get(chapano=n.se_check_by_qa)
            se_check_by_qa_name = e.lastname + ', ' + e.firstname + ' ' + e.middlename
        except Employee.DoesNotExist:
            se_check_by_qa_name = 'unknown'

    sqlStmt = """SELECT d.phase as phase, d.reason as reason, DATE_FORMAT(d.denied_date, '%M %d, %Y') as denied_date, 
        concat(e.lastName, ', ' ,  e.firstName, ' ' ,  e.middleName) as denied_by_name
        FROM DENY_REASON d
        LEFT JOIN EMPLOYEE e ON (d.denied_by =  e.chapaNo)
        WHERE d.accepted_date is null """ 
        
    sqlStmt = sqlStmt + " and d.ncr_no = '" + ncr_no + "' and d.rev_no = '" + str(n.rev_no) + "'"   
    
    
    with connection.cursor() as c:
        c.execute(sqlStmt)
        deny_reasonB_data = namedtuplefetchall(c)   
        
        
        phase = ''
        
        for rec in deny_reasonB_data:
            phase = str(rec[0])
            reason = str(rec[1])
            
            if phase == 'A':
                deny_reasonA = reason  
                is_denied_A = 1 

            elif phase == 'B':
                deny_reasonB = reason  
                is_denied_B = 1 
                
            elif phase == 'C':
                deny_reasonC = reason      
                is_denied_C = '1'             
                if n.ca_description not in [None, '']:
                    is_denied_D = '1' 
                
            elif phase == 'D':
                deny_reasonD = reason  
                is_denied_C = '1'             
                is_denied_D = '1'
                
            elif phase == 'E' :
                deny_reasonE = reason  
                is_denied_C = '1'             
                is_denied_D = '1'
                is_denied_E = '1'
                
                if n.se_description not in [None, '']:
                    is_denied_F = '1'
                
            elif phase == 'F':
                deny_reasonF = reason  
                is_denied_C = '1'             
                is_denied_D = '1'
                is_denied_E = '1'
                is_denied_F = '1'
                
                    
    

        
    
    ncr_no_size = 'S'
    if len(ncr_no) > 25:     
        ncr_no_size = 'L'
                
    array = n.nc_discovered_by.split("||")
    nc_discoverer_email = ''
    nc_discovered_by = array[0]


    try:
        nc_discoverer_email = array[1]
    except:
        pass

    form = NCRCreateForm(initial={                
            'ncr_no' : n.ncr_no, 
            'ncr_issue_date' : ncr_issue_date, 
            #'dept' : n.dept, 
            #'project' : n.project.id, 
            'source' : n.source, 
            'other_source' : n.other_source, 
            'classification' : n.classification,                 
            'nc_detail_description' : n.nc_detail_description,
            
            #Start 2024/05/09
            'nc_discovered_by' : nc_discovered_by,
            'nc_discoverer_email': nc_discoverer_email,
            'nc_conformed_by' : n.nc_conformed_by, 
            'nc_conformed_date' : nc_conformed_date,
            'ic_description' : n.ic_description, 
            'ic_incharge' : n.ic_incharge, 
            'ic_create_date' : ic_create_date, 
            #'ic_approve_by' : ic_approve_by,
            'ic_approve_date' : ic_approve_date, 
            #'rca_description' : newVal_rca_description,
            'ca_necessary' : n.ca_necessary, 
            #'rca_incharge' : rca_incharge, 
            'rca_create_date' : rca_create_date, 
            #'rca_approve_by' : rca_approve_by, 
            'rca_approve_date' : rca_approve_date, 
            'ca_target_date' : n.ca_target_date, 
            'ca_description' : n.ca_description, 
            'ca_create_by' : n.ca_create_by, 
            'ca_create_date' : ca_create_date, 
            #'ca_checked_by_sh' : ca_checked_by_sh, 
            'ca_check_date_by_sh' : ca_check_date_by_sh, 
            'ca_approved_by_mgr' : n.ca_approved_by_mgr, 
            'ca_approved_date_by_mgr' : ca_approved_date_by_mgr, 
            'ra_description' : n.ra_description, 
            'ra_action_effective' : n.ra_action_effective, 
            'ra_followup_date' : n.ra_followup_date,
            #'ra_check_by_staff' : ra_check_by_staff,  
            'ra_check_date_by_staff' : ra_check_date_by_staff, 
            #'ra_check_by_sh' : ra_check_by_sh, 
            'ra_check_date_by_sh' : ra_check_date_by_sh, 
            'se_description' : n.se_description, 
            'se_ro_updated' : n.se_ro_updated,  
            'se_check_by_mgr' : n.se_check_by_mgr, 
            'se_check_date_by_mgr' : se_check_date_by_mgr, 
            'se_check_by_qa' : n.se_check_by_qa, 
            'se_check_date_by_qa' : se_check_date_by_qa,
            #'hidden_dept_id' : n.dept.id, 
            'hidden_mail_sent_date_1' : n.mail_sent_date_1,  
            'hidden_mail_sent_date_2' : n.mail_sent_date_2,
            'hidden_mail_sent_date_3' : n.mail_sent_date_3,
            'hidden_update_date' : n.update_date,
            'nc_conforme_status' : n.nc_conforme_status,
            'ic_approve_status' : n.ic_approve_status,
            'rca_approve_status' : n.rca_approve_status,
            'ca_check_by_sh_status' : n.ca_check_by_sh_status,
            'ca_approve_by_mgr_status' : n.ca_approve_by_mgr_status,
            'ra_check_by_staff_status' : n.ra_check_by_staff_status,
            'ra_check_by_sh_status' : n.ra_check_by_sh_status,
            'se_check_by_mgr_status' : n.se_check_by_mgr_status,
            'se_check_by_qa_status' : n.se_check_by_qa_status,
            'rev_no' : n.rev_no,                    
            'is_denied_A' : is_denied_A,
            'is_denied_B' : is_denied_B,
            'is_denied_C' : is_denied_C,
            'is_denied_D' : is_denied_D,
            'is_denied_E' : is_denied_E,
            'is_denied_F' : is_denied_F,
            'status' : n.status,
            'comments' : n.comments,
            'is_A_on_edit_mode' : 'X',
            'is_B_on_edit_mode' : 'X',
            'is_C_on_edit_mode' : 'X',
            'is_D_on_edit_mode' : 'X',
            'is_E_on_edit_mode' : 'X',
            'is_F_on_edit_mode' : 'X',
            'ra_check_by_staff_name' : ra_check_by_staff_name,
            })
    
    
    context = {
               'logged': logged,
               'nc_discoverer_email':nc_discoverer_email,
               'nc_discovered_by':nc_discovered_by,
               'max_rev': max_rev,
               'pageType':pageType,
               #'data2':NcrDetailMstrHistory,
               'ncr_no_size':ncr_no_size,
               'iterator': range(int(max_rev)),
               'form' : form,
               'data' : n, 
               'nc_conformed_by_name' : nc_conformed_by_name,   
               'ic_approve_by_name' : ic_approve_by_name,   
               'rca_approve_by_name' : rca_approve_by_name,
               'ca_checked_by_sh_name' :ca_checked_by_sh_name,
               'ra_check_by_sh_name' : ra_check_by_sh_name,
               'ic_incharge_name' : ic_incharge_name,
               'rca_incharge_name' : rca_incharge_name, 
               'ra_check_by_staff_name' : ra_check_by_staff_name, 
               'ca_approved_by_mgr_name' : ca_approved_by_mgr_name,
               'se_check_by_mgr_name' : se_check_by_mgr_name,
               'se_check_by_qa_name' : se_check_by_qa_name,
               'deny_reasonA' : deny_reasonA, 
               'deny_reasonB' : deny_reasonB, 
               'deny_reasonC' : deny_reasonC, 
               'deny_reasonD' : deny_reasonD, 
               'deny_reasonE' : deny_reasonE, 
               'deny_reasonF' : deny_reasonF,
               'is_denied_A' : is_denied_A,
               'is_denied_B' : is_denied_B,
               'is_denied_C' : is_denied_C,
               'is_denied_D' : is_denied_D,
               'is_denied_E' : is_denied_E,
               'is_denied_F' : is_denied_F,
               "isChecker" : isChecker,
               "isSH" : isSH,
               "isGrpMgr" : isGrpMgr,
               "isAdmin" : isAdmin,
               'hidden_update_user_id1' : n.update_user_id,
               'logged_username' : logged_username,
               'logged_user_chapa_no' : logged_user_chapa_no,
               }

    print('END : ncr_create_view_history')
    return render(request, template_name, context) 




