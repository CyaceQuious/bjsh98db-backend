from django.urls import path, include
import Query.views as views

urlpatterns = [
    path('query', views.query, name = 'query'),
    path('query_meet_list',views.query_meet_list, name = 'query_meet_list'),
    path('query_project_list',views.query_project_list, name = 'query_project_list'),
    path('query_project_zubie_list',views.query_project_zubie_list, name = 'query_project_zubie_list'),
    path('query_meet_name',views.query_meet_name, name = 'query_meet_name'),
    path('query_team_score',views.query_team_score,name = 'query_team_score'),
    path('query_personal_web',views.query_personal_web,name = 'query_personal_web'),
    path('manage_meet',views.manage_meet, name = 'manage_meet'),
    path('manage_project',views.manage_project, name = 'manage_project'),
    path('manage_result',views.manage_result,name = 'manage_result'),
    path('update_new_result_from_online',views.update_new_result_from_online,name = 'update_new_result_from_online'),
    path('update_new_meet_from_online',views.update_new_meet_from_online,name = 'update_new_meet_from_online'),
   # path('query_my',views.query_my,name = 'query_my')
]

