from django.urls import path,include
from .views import home, about, contact,logout_view
from . import views
from .views import  view_audit_logs,verify_candidate,candidate_dashboard,candidate_profile, update_candidate_profile, candidate_audit_logs
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'), 
    path('custom-admin-login/', views.admin_login, name='admin_login'),
    path('custom-admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('custom-admin/dashboard/<int:election_id>/', views.admin_dashboard, name='admin_dashboard_with_id'),
    path('logout/', logout_view, name='logout'),
    path('elections/', views.list_elections, name='list_elections'),
    path('elections/create/', views.create_election, name='create_election'),
    path('elections/<int:election_id>/edit/', views.update_election, name='update_election'),
    path('elections/<int:election_id>/delete/', views.delete_election, name='delete_election'),
    path('candidates/', views.candidate_list, name='candidate_list'),
    path('candidates/add/', views.candidate_create, name='candidate_create'),
    path('candidates/<int:pk>/edit/', views.candidate_update, name='candidate_update'),
    path('candidates/<int:pk>/delete/', views.candidate_delete, name='candidate_delete'),
    path('dashboard/', views.candidate_dashboard, name='candidate_dashboard'),
    path('profile/audit-logs/', candidate_audit_logs, name='candidate_audit_logs'),
    path('eligible-elections/<int:id>/', views.eligible_elections, name='eligible_elections'),
    path('credentials', views.update_credentials, name='update_credentials'),
    path('submit-nomination/<int:election_id>/', views.submit_nomination, name='submit_nomination'),
    path('view-results/', views.view_results, name='view_results'),
    path('results/<int:election_id>/', views.result_detail, name='result_detail'),
    path('calculate-all-results/', views.calculate_all_results, name='calculate_all_results'),

    path('candidate-registration/', views.candidate_registration, name='candidate_registration'),
    path('candidate/<int:id>/verify/', verify_candidate, name='verify_candidate'),
    path('candidate-login/', views.candidate_login, name='candidate_login'),
    path('profile/', candidate_profile, name='candidate_profile'),
    path('profile/update/', update_candidate_profile, name='update_candidate_profile'), 
    path('audit-logs/', view_audit_logs, name='audit_logs'),
    path('voter-registration/', views.voter_registration, name='voter_registration'),
    path('voter-dashboard/', views.voter_dashboard, name='voter_dashboard'),
    path('verify-voter/<int:id>/', views.verify_voter, name='verify_voter'),
    path('voters/', views.voter_list, name='voter_list'),
    path('voter_profile/<int:id>/', views.voter_profile, name='voter_profile'),
    path('update_voter_profile/<int:id>/', views.update_voter_profile, name='update_voter_profile'),
    path('voter-login/', views.voter_login, name='voter_login'),
    path('update_voter_credentials/<int:id>/', views.update_voter_credentials, name='update_voter_credentials'),
    path('voters/<int:id>/delete/', views.voter_delete, name='voter_delete'),
    path('election/<int:election_id>/vote/', views.cast_vote, name='cast_vote'),
    path('election/<int:election_id>/candidates/', views.view_candidates, name='view_candidates'),
    path('candidate/<int:candidate_id>/',views.candidate_detail, name='candidate_detail'),
    path('generate_report/', views.generate_report, name='generate_report'),
    path('download_report/<int:report_id>/', views.download_report, name='download_report'),
    path('reports/', views.report_list, name='report_list'),
    path('voter/audit-logs/', views.voter_audit_logs, name='voter_audit_logs'),
    path('submit-feedback/', views.submit_feedback, name='submit_feedback'),
    path('view-feedback/', views.view_feedback, name='view_feedback'),
    path('send-otp/', views.send_otp_request, name='send_otp'),
    path("live-results/", views.live_results, name="live_results"),
    
]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
