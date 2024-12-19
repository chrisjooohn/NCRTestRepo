"""
Created on Wed March 20 16:21:40 2024

@author: ec.marinas
"""

from dateutil import relativedelta
from datetime import date
from datetime import datetime
import mysql.connector
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#For real server (Deployment)
#PROJ_URL = 'http://mgmntsystem.sdmi.shi.co.jp/ncr/'
#PROJ_URL = 'http://127.0.0.1:8081/ncr/' (old)
PROJ_URL = 'http://127.0.0.1:8080/ncr/'

mydb = mysql.connector.connect(
    host = '10.2.1.18',
    user = 'otuser02',
    password = 'otuser02',
    database = "ot",
    port = '3306'   
)

mycursor = mydb.cursor()
current_date = date.today()
current_date = datetime.strptime(str(current_date),"%Y-%m-%d")
mailFrom = 'NCR_Mgnt_Sys@shi-g.com'



def update_Date():
    current_time = datetime.now()
    print(current_time)

    #select all status that isnt closed or cancelled
    #mycursor.execute("SELECT * FROM `ncr_detail_mstr` WHERE status not in ('2','7')  ")



    #Test for only one ncr
    mycursor.execute("SELECT * FROM `ncr_detail_mstr` WHERE ncr_no = 'NCR-2024-03-21-BA-01-0073'  ")

    myresult = mycursor.fetchall()

    for x in myresult:
        denyReason = False
        reason = ''
        accepted_date = ''

        ncr_no = x[0]
        nc_conformed_by = x[9]
        nc_conformed_date= x[10]
        ic_incharge = x[13]
        ic_create_date = x[14]
        ic_approve_by = x[15]
        ic_approve_date = x[16] 
        rca_incharge = x[19]
        rca_create_date = x[20]
        rca_approve_by = x[21]
        rca_approve_date = x[22]
        ca_create_by = x[25]
        ca_create_date = x[26]
        ca_checked_by_sh = x[27]
        ca_check_date_by_sh = x[29]
        ca_approved_by_mgr = x[28]
        ca_approved_date_by_mgr = x[30]
        ra_check_by_staff = x[34]
        ra_check_date_by_staff = x[35]
        ra_check_by_sh = x[36]
        ra_check_date_by_sh = x[37] 
        se_check_by_mgr = x[40]   
        se_check_date_by_mgr = x[41]  
        se_check_by_qa = x[42]   
        se_check_date_by_qa = x[43]
        status = x[47]
        update_date = x[58]
        update_user_id = x[57]
        DEADLINE = x[48]

        update_date = str(update_date).split()
        update_date = update_date[0]

        update_date = datetime.strptime(str(update_date),"%Y-%m-%d")
        difference = relativedelta.relativedelta(current_date,update_date)

        years = int(difference.years)
        months = int(difference.months)
        days = int(difference.days)        

        mycursor.execute("SELECT reason,accepted_date FROM `deny_reason` WHERE ncr_no = '" + ncr_no + "' ORDER BY phase DESC LIMIT 1")
        deny_reason = mycursor.fetchall()
        for x in deny_reason:

            reason = x[0]
            accepted_date = x[1]

        if reason not in ('', None):
            if accepted_date == None:
                print(accepted_date)
                denyReason = True
            elif accepted_date not in ('', None):
                denyReason = False
        else:
            denyReason = False

        if days >= 2:

            if denyReason == True:
                receiver = ic_incharge

            elif status == '3':
                receiver = ic_incharge

            else:
                receiver = ''
                if se_check_date_by_qa not in ('', None):
                    receiver = ic_incharge
                    print("-1")
                elif se_check_date_by_mgr not in ('', None):
                    receiver = se_check_by_qa     
                    print("-2")
                elif ra_check_date_by_sh not in ('', None):
                    receiver = se_check_by_mgr
                    print("-3")
                elif ra_check_date_by_staff not in ('', None):
                    receiver = ra_check_by_sh
                    print("-4")                    
                elif ca_approved_date_by_mgr not in ('', None):
                    receiver = ic_incharge
                    print("-5")
                elif ca_check_date_by_sh not in ('', None):
                    print("-6")
                    receiver = ca_approved_by_mgr  
                elif rca_approve_date not in ('', None):
                    print("-7")
                    if ca_checked_by_sh not in ('', None):
                        receiver = ca_checked_by_sh
                    else:
                        receiver = ic_incharge
                elif rca_create_date not in ('', None):
                    print("-8")
                    receiver = rca_approve_by
                elif ic_approve_date not in ('', None):
                    print("-9")
                    receiver = ic_incharge
                elif ic_create_date not in ('', None):
                    print("-10")
                    receiver = ic_approve_by
                elif nc_conformed_date not in ('', None):
                    print("-11")
                    if ic_incharge not in ('', None):
                        receiver = ic_incharge
                    else:
                        receiver = nc_conformed_by
                else:
                    print("-12")
                    receiver = nc_conformed_by

            print(ncr_no)
            DateCompare(years,months,days,receiver,ncr_no,update_date,DEADLINE)

        else:
            print("")
    return

def DateCompare(years,months,days,receiver,ncr_no,update_date,DEADLINE):

    email = ""
    #firstName = ""

    print(">>>>>>>>"+str(receiver))

    try:
        mycursor.execute("SELECT firstName,email FROM `employee` WHERE chapano = '" + receiver + "'  ")
        myresult = mycursor.fetchall()
        for x in myresult:
            #firstName = str(x[0])
            email = str(x[1])

    except:
        #firstName = ""
        email = ""

    if email not in ('', None):
        if years > 0:
            message = str(years) +" year/s "
        elif months > 0:
            message = str(months) +" Month/s "
        elif days >= 2:
            message =  str(days) +" Days"
        else:
            message = ""

        try:
            if message not in ('', None):
                mailTo = email
                msg = MIMEMultipart()
                msg ['From'] = mailFrom
                msg ['To'] = mailTo
                msg ['Subject'] = " 【" + str(message) + "】 NO RESPONSE REMINDER NCR: 【" + str(ncr_no) + "】"

                body = f"""Sir/Madam,<br/><br/>
                Please be informed of the following NCR: {str(ncr_no)}.<br/>
                You might have missed in the correspondence of the said NCR.
                Kindly continue the NCR on or before its deadline on """+ str(DEADLINE) +"""
                See the details via this link: <br/>""" + PROJ_URL + """ncr_verify_view_via_mail/"""+ncr_no+"""/""""""<br/><br/>
                This message is automatically generated by the NCR WebApp System."""

                msg.attach(MIMEText(body, 'html'))

                smtpObj = smtplib.SMTP('mx1.shi.co.jp', 25)
                text = msg.as_string()

                try:
                    smtpObj.sendmail(mailFrom, mailTo, text)
                except:
                    print("ERROR")

            else:
                print("")

        except:
            print("ERROR")

    return 

update_Date()