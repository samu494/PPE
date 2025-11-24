from django.urls import path
from . import views
from . import admin_views
from . import payment_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.admin.views.decorators import staff_member_required

urlpatterns = [
    # Pages principales
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('comment-ca-marche/', views.how_it_works, name='how_it_works'),
    path('choisir-role/', views.role_selection, name='role_selection'),
    path('guide-premiere-fois/', views.first_time_guide, name='first_time_guide'),
    
    # Authentification
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('signup/client/', views.signup_client, name='signup_client'),
    path('signup/freelancer/', views.signup_freelancer, name='signup_freelancer'),
    path('complete-profile/', views.complete_profile, name='complete_profile'),
    
    # Dashboard et profil
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Projets
    path('projects/', views.projects_list, name='projects_list'),
    path('projects/create/', views.create_project, name='create_project'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('projects/<int:project_id>/propose/', views.submit_proposal, name='submit_proposal'),
    
    # Freelances
    path('freelancers/', views.freelancers_list, name='freelancers_list'),
    path('freelancers/<int:freelancer_id>/', views.freelancer_detail, name='freelancer_detail'),
    
    # Messages
    path('messages/', views.messages_list, name='messages_list'),
    path('messages/<int:user_id>/', views.conversation, name='conversation'),
    path('messages/start/<int:user_id>/', views.start_conversation, name='start_conversation'),
    
    # API Endpoints
    path('api/notifications/', views.api_notifications, name='api_notifications'),
    path('api/mark-notification-read/', views.api_mark_notification_read, name='api_mark_notification_read'),
    path('api/search-suggestions/', views.api_search_suggestions, name='api_search_suggestions'),
    
    # Support client
    path('support/', views.support_tickets, name='support_tickets'),
    path('support/create/', views.create_support_ticket, name='create_support_ticket'),
    path('support/<int:ticket_id>/', views.support_ticket_detail, name='support_ticket_detail'),
    path('support/<int:ticket_id>/close/', views.close_support_ticket, name='close_support_ticket'),
    
    # Administration
    path('admin/support/', staff_member_required(views.admin_support_tickets), name='admin_support_tickets'),
    path('admin/proposals/', staff_member_required(views.admin_validate_proposals), name='admin_validate_proposals'),
    path('admin/proposals/<int:proposal_id>/', staff_member_required(views.admin_validate_proposal), name='admin_validate_proposal'),
    path('admin/dashboard/', staff_member_required(admin_views.admin_dashboard), name='admin_dashboard'),
    path('admin/statistics/', staff_member_required(admin_views.admin_statistics), name='admin_statistics'),
    
    # Paiements
    path('payment/methods/', payment_views.payment_methods, name='payment_methods'),
    path('payment/process/<int:project_id>/', payment_views.process_payment, name='process_payment'),
    path('payment/crypto/<int:payment_id>/', payment_views.crypto_payment, name='crypto_payment'),
    path('payment/mobile-money/<int:payment_id>/', payment_views.mobile_money_payment, name='mobile_money_payment'),
    path('payment/paypal/<int:payment_id>/', payment_views.paypal_payment, name='paypal_payment'),
    path('payment/card/<int:payment_id>/', payment_views.card_payment, name='card_payment'),
    path('payment/bank-transfer/<int:payment_id>/', payment_views.bank_transfer_payment, name='bank_transfer_payment'),
    path('payment/success/<int:payment_id>/', payment_views.payment_success, name='payment_success'),
    path('payment/failed/<int:payment_id>/', payment_views.payment_failed, name='payment_failed'),
    path('webhook/payment/', payment_views.payment_webhook, name='payment_webhook'),
    path('payment/validate/<int:payment_id>/', payment_views.validate_payment_api, name='validate_payment_api'),
    path('payment/reject/<int:payment_id>/', payment_views.reject_payment_api, name='reject_payment_api'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)