from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import redirect
from main.admin_views import admin_dashboard, admin_statistics

class FreeAfriqueAdminSite(AdminSite):
    """Site d'administration personnalisé pour FreeAfrique"""
    
    site_header = "Administration FreeAfrique"
    site_title = "FreeAfrique Admin"
    index_title = "Tableau de bord FreeAfrique"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(admin_dashboard), name='admin_dashboard'),
            path('statistics/', self.admin_view(admin_statistics), name='admin_statistics'),
        ]
        return custom_urls + urls
    
    def index(self, request, extra_context=None):
        """Redirige vers le tableau de bord personnalisé"""
        return redirect('admin_dashboard')

# Configuration des actions en lot
def make_verified(modeladmin, request, queryset):
    queryset.update(is_verified=True)
make_verified.short_description = "Marquer comme vérifié"

def make_unverified(modeladmin, request, queryset):
    queryset.update(is_verified=False)
make_unverified.short_description = "Marquer comme non vérifié"

def make_featured(modeladmin, request, queryset):
    queryset.update(is_featured=True)
make_featured.short_description = "Mettre en avant"

def make_unfeatured(modeladmin, request, queryset):
    queryset.update(is_featured=False)
make_unfeatured.short_description = "Retirer de la mise en avant"

def approve_proposals(modeladmin, request, queryset):
    from django.utils import timezone
    queryset.update(admin_validation='approved', status='pending', validated_by=request.user, validation_date=timezone.now())
approve_proposals.short_description = "Approuver les propositions sélectionnées"

def reject_proposals(modeladmin, request, queryset):
    from django.utils import timezone
    queryset.update(admin_validation='rejected', status='rejected', validated_by=request.user, validation_date=timezone.now())
reject_proposals.short_description = "Rejeter les propositions sélectionnées"

def mark_tickets_resolved(modeladmin, request, queryset):
    queryset.update(status='resolved')
mark_tickets_resolved.short_description = "Marquer comme résolu"

def mark_tickets_closed(modeladmin, request, queryset):
    queryset.update(status='closed')
mark_tickets_closed.short_description = "Marquer comme fermé"

def assign_tickets_to_me(modeladmin, request, queryset):
    queryset.update(assigned_to=request.user)
assign_tickets_to_me.short_description = "S'assigner les tickets sélectionnés"

# Configuration des filtres personnalisés
class IsVerifiedFilter(admin.SimpleListFilter):
    title = 'Statut de vérification'
    parameter_name = 'is_verified'
    
    def lookups(self, request, model_admin):
        return (
            ('yes', 'Vérifié'),
            ('no', 'Non vérifié'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(is_verified=True)
        if self.value() == 'no':
            return queryset.filter(is_verified=False)

class IsFeaturedFilter(admin.SimpleListFilter):
    title = 'Mise en avant'
    parameter_name = 'is_featured'
    
    def lookups(self, request, model_admin):
        return (
            ('yes', 'Mis en avant'),
            ('no', 'Non mis en avant'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(is_featured=True)
        if self.value() == 'no':
            return queryset.filter(is_featured=False)

class AdminValidationFilter(admin.SimpleListFilter):
    title = 'Validation admin'
    parameter_name = 'admin_validation'
    
    def lookups(self, request, model_admin):
        return (
            ('pending', 'En attente'),
            ('approved', 'Approuvée'),
            ('rejected', 'Rejetée'),
        )
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(admin_validation=self.value())

class TicketStatusFilter(admin.SimpleListFilter):
    title = 'Statut du ticket'
    parameter_name = 'ticket_status'
    
    def lookups(self, request, model_admin):
        return (
            ('open', 'Ouvert'),
            ('in_progress', 'En cours'),
            ('waiting', 'En attente'),
            ('resolved', 'Résolu'),
            ('closed', 'Fermé'),
        )
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())

# Configuration des champs de recherche personnalisés
class FreelancerSearchMixin:
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'location', 'skills']
    list_filter = [IsVerifiedFilter, IsFeaturedFilter, 'availability_status', 'rating', 'experience_years', 'created_at']

class ClientSearchMixin:
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'company_name', 'location']
    list_filter = [IsVerifiedFilter, 'created_at']

class ProjectSearchMixin:
    search_fields = ['title', 'description', 'client__user__first_name', 'client__user__last_name', 'category__name']
    list_filter = ['status', 'category', 'budget_type', IsFeaturedFilter, 'is_urgent', 'created_at']

class ProposalSearchMixin:
    search_fields = ['project__title', 'freelancer__user__first_name', 'freelancer__user__last_name']
    list_filter = ['status', AdminValidationFilter, IsFeaturedFilter, 'created_at']

class SupportTicketSearchMixin:
    search_fields = ['subject', 'description', 'user__first_name', 'user__last_name', 'user__email']
    list_filter = [TicketStatusFilter, 'priority', 'ticket_type', 'created_at']

# Configuration des actions en lot par modèle
FREELANCER_ACTIONS = [make_verified, make_unverified, make_featured, make_unfeatured]
CLIENT_ACTIONS = [make_verified, make_unverified]
PROJECT_ACTIONS = [make_featured, make_unfeatured]
PROPOSAL_ACTIONS = [approve_proposals, reject_proposals, make_featured, make_unfeatured]
SUPPORT_TICKET_ACTIONS = [mark_tickets_resolved, mark_tickets_closed, assign_tickets_to_me]

# Configuration des champs en lecture seule
READONLY_FIELDS = {
    'Freelancer': ['rating', 'total_reviews', 'completed_projects', 'total_earnings'],
    'Client': ['total_projects', 'total_spent'],
    'Project': ['views_count', 'proposals_count'],
    'Proposal': ['created_at', 'validation_date'],
    'Payment': ['project', 'client', 'freelancer', 'amount', 'payment_method', 'status', 'transaction_id', 'description'],
    'Notification': ['recipient', 'notification_type', 'title', 'message', 'related_object_id', 'related_object_type'],
    'Dispute': ['project', 'initiator', 'reason', 'description', 'evidence'],
}

# Configuration des champs éditables en liste
LIST_EDITABLE_FIELDS = {
    'Category': ['is_featured'],
    'Skill': ['is_popular'],
    'Freelancer': ['is_verified', 'is_featured', 'availability_status'],
    'Client': ['is_verified'],
    'Project': ['is_featured', 'is_urgent', 'status'],
    'Proposal': ['is_featured'],
    'Review': ['is_public'],
    'Notification': ['is_read', 'is_important'],
    'Milestone': ['status'],
    'Dispute': ['status'],
    'SupportTicket': ['status', 'assigned_to'],
}

