from django.urls import path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

app_name = 'NCRMgmntSystem'

urlpatterns = [
              path('', views.login_view, name='login_view'),
              path('login', views.login, name='login'),
              path('logout', views.logout, name='logout'),
              path('ncr_search_view', views.ncr_search_view, name='ncr_search_view'),
              path('ncr_create_view_ins', views.ncr_create_view_ins, name='ncr_create_view_ins'),       
              path('ncr_create', views.ncr_create, name='ncr_create'),       
              path('ajax/load-projects/', views.load_projects, name='ajax_load_projects'), 
              path('ajax/load-members/', views.load_members, name='ajax_load_members'),  
              path('ajax/load-checkers/', views.load_checkers, name='ajax_load_checkers'),              
              path('ncr_create_view_upd/<str:ncr_no>/<str:status>', views.ncr_create_view_upd, name='ncr_create_view_upd'),
              path('ncr_create_view_upd_via_mail/<str:ncr_no>/<str:user_id>', views.ncr_create_view_upd_via_mail, name='ncr_create_view_upd_via_mail'),
              path('ncr_verify_view/<str:ncr_no>/<str:check_phase>/<str:message>/<str:error_message>/<str:from_email_id>', views.ncr_verify_view, name='ncr_verify_view'),
              path('ncr_verify_view_via_mail/<str:ncr_no>/<str:user_id>', views.ncr_verify_view_via_mail, name='ncr_verify_view_via_mail'),
              path('ncr_verify_accept', views.ncr_verify_accept, name='ncr_verify_accept'),
              path('ncr_verify_list_view', views.ncr_verify_list_view, name='ncr_verify_list_view'),
              path('ncr_create_view', views.ncr_create_view, name='ncr_create_view'),
              path('project_add', views.project_add, name='project_add'),  
              path('projects_show', views.projects_show, name='projects_show'),  
              path('project_update_view/<int:id>', views.project_update_view),  
              path('project_update/<int:id>', views.project_update, name='project_update'),  
              #path('project_delete/<int:id>', views.project_delete, name='project_delete'),  
              path('ncr_search_view_init', views.ncr_search_view_init, name='ncr_search_view_init'),
              path('ajax/get-latest-update_date/', views.get_latest_update_date, name='ajax_get_latest_update_date'), 
              path('employee_password_change_view/<str:chapano>', views.employee_password_change_view, name='employee_password_change_view'),
              path('employee_password_change/<str:chapano>', views.employee_password_change, name='employee_password_change'), 
              
              
              path('project_delete/<int:id>/<str:sectionCode>/<str:projectCode>/<int:page>', views.project_delete, name='project_delete'),  
              
              
              
              #start adding 2024/04/16 Edric
              path('check_project_NCR/', views.check_project_NCR, name='check_project_NCR'),
              
              #2024/05/01
              path('ncr_create_view_history/<str:ncr_no>/<str:rev_no>/<str:pageType>', views.ncr_create_view_history, name='ncr_create_view_history'),
              ]


urlpatterns += staticfiles_urlpatterns()
