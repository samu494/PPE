from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Avg
from .models import Category, Freelancer, Client, Project, Proposal, Review, Message, Notification, Payment, Milestone, Dispute, Skill, SupportTicket, TicketResponse
from .payment_models import PaymentMethod, CryptoPayment, MobileMoneyPayment, PayPalPayment, PaymentGateway, PaymentTransaction

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'freelancer_count', 'project_count', 'is_featured', 'created_at', 'color_display']
    search_fields = ['name', 'description']
    list_filter = ['is_featured', 'created_at']
    ordering = ['-is_featured', 'name']
    list_editable = ['is_featured']
    
    def color_display(self, obj):
        return format_html('<div style="width: 20px; height: 20px; background-color: {}; border-radius: 3px;"></div>', obj.color)
    color_display.short_description = 'Couleur'

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_popular', 'created_at']
    search_fields = ['name']
    list_filter = ['category', 'is_popular', 'created_at']
    ordering = ['-is_popular', 'name']
    list_editable = ['is_popular']

@admin.register(Freelancer)
class FreelancerAdmin(admin.ModelAdmin):
    list_display = ['user', 'hourly_rate', 'rating', 'total_reviews', 'completed_projects', 'is_verified', 'is_featured', 'availability_status', 'location']
    list_filter = ['is_verified', 'is_featured', 'availability_status', 'rating', 'experience_years', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'location']
    readonly_fields = ['rating', 'total_reviews', 'completed_projects', 'total_earnings']
    ordering = ['-rating', '-created_at']
    list_editable = ['is_verified', 'is_featured', 'availability_status']
    actions = ['verify_freelancers', 'unverify_freelancers', 'feature_freelancers', 'unfeature_freelancers']
    
    fieldsets = (
        ('Informations utilisateur', {
            'fields': ('user', 'profile_picture')
        }),
        ('Informations professionnelles', {
            'fields': ('hourly_rate', 'description', 'skills', 'experience_years', 'education', 'languages')
        }),
        ('Localisation et contact', {
            'fields': ('location', 'portfolio_link')
        }),
        ('Statut et vérification', {
            'fields': ('is_verified', 'is_featured', 'availability_status')
        }),
        ('Statistiques', {
            'fields': ('rating', 'total_reviews', 'completed_projects', 'total_earnings'),
            'classes': ('collapse',)
        })
    )
    
    def verify_freelancers(self, request, queryset):
        queryset.update(is_verified=True)
    verify_freelancers.short_description = "Vérifier les freelances sélectionnés"
    
    def unverify_freelancers(self, request, queryset):
        queryset.update(is_verified=False)
    unverify_freelancers.short_description = "Dévérifier les freelances sélectionnés"
    
    def feature_freelancers(self, request, queryset):
        queryset.update(is_featured=True)
    feature_freelancers.short_description = "Mettre en avant les freelances sélectionnés"
    
    def unfeature_freelancers(self, request, queryset):
        queryset.update(is_featured=False)
    unfeature_freelancers.short_description = "Retirer de la mise en avant"

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['user', 'company_name', 'is_verified', 'total_projects', 'total_spent', 'created_at']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'company_name', 'location']
    readonly_fields = ['total_projects', 'total_spent']
    list_editable = ['is_verified']
    actions = ['verify_clients', 'unverify_clients']
    
    fieldsets = (
        ('Informations utilisateur', {
            'fields': ('user', 'profile_picture')
        }),
        ('Informations entreprise', {
            'fields': ('company_name', 'company_description', 'website')
        }),
        ('Localisation', {
            'fields': ('location',)
        }),
        ('Statut', {
            'fields': ('is_verified',)
        }),
        ('Statistiques', {
            'fields': ('total_projects', 'total_spent'),
            'classes': ('collapse',)
        })
    )
    
    def verify_clients(self, request, queryset):
        queryset.update(is_verified=True)
    verify_clients.short_description = "Vérifier les clients sélectionnés"
    
    def unverify_clients(self, request, queryset):
        queryset.update(is_verified=False)
    unverify_clients.short_description = "Dévérifier les clients sélectionnés"

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'client', 'category', 'budget_display', 'status', 'is_featured', 'is_urgent', 'views_count', 'proposals_count', 'created_at']
    list_filter = ['status', 'category', 'budget_type', 'is_featured', 'is_urgent', 'created_at']
    search_fields = ['title', 'description', 'client__user__first_name', 'client__user__last_name']
    readonly_fields = ['views_count', 'proposals_count']
    date_hierarchy = 'created_at'
    ordering = ['-is_featured', '-created_at']
    list_editable = ['is_featured', 'is_urgent', 'status']
    actions = ['feature_projects', 'unfeature_projects', 'mark_urgent', 'unmark_urgent']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('title', 'description', 'category', 'client')
        }),
        ('Budget et délais', {
            'fields': ('budget_min', 'budget_max', 'budget_type', 'deadline')
        }),
        ('Compétences requises', {
            'fields': ('required_skills', 'additional_info')
        }),
        ('Statut et visibilité', {
            'fields': ('status', 'is_featured', 'is_urgent')
        }),
        ('Statistiques', {
            'fields': ('views_count', 'proposals_count', 'selected_freelancer'),
            'classes': ('collapse',)
        }),
        ('Fichiers', {
            'fields': ('attachments',),
            'classes': ('collapse',)
        })
    )
    
    def budget_display(self, obj):
        return f"{obj.budget_min}€ - {obj.budget_max}€"
    budget_display.short_description = 'Budget'
    
    def feature_projects(self, request, queryset):
        queryset.update(is_featured=True)
    feature_projects.short_description = "Mettre en avant les projets sélectionnés"
    
    def unfeature_projects(self, request, queryset):
        queryset.update(is_featured=False)
    unfeature_projects.short_description = "Retirer de la mise en avant"
    
    def mark_urgent(self, request, queryset):
        queryset.update(is_urgent=True)
    mark_urgent.short_description = "Marquer comme urgent"
    
    def unmark_urgent(self, request, queryset):
        queryset.update(is_urgent=False)
    unmark_urgent.short_description = "Retirer le statut urgent"

@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ['project', 'freelancer', 'price', 'delivery_time', 'status', 'admin_validation', 'validated_by', 'is_featured', 'created_at']
    list_filter = ['status', 'admin_validation', 'is_featured', 'created_at']
    search_fields = ['project__title', 'freelancer__user__first_name', 'freelancer__user__last_name']
    readonly_fields = ['created_at', 'validation_date']
    ordering = ['-is_featured', '-created_at']
    list_editable = ['is_featured']
    actions = ['approve_proposals', 'reject_proposals', 'feature_proposals', 'unfeature_proposals']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('project', 'freelancer')
        }),
        ('Proposition', {
            'fields': ('price', 'delivery_time', 'message', 'additional_info')
        }),
        ('Validation', {
            'fields': ('status', 'admin_validation', 'admin_comment', 'validated_by', 'validation_date')
        }),
        ('Visibilité', {
            'fields': ('is_featured',)
        }),
        ('Fichiers', {
            'fields': ('attachments',),
            'classes': ('collapse',)
        })
    )
    
    def approve_proposals(self, request, queryset):
        from django.utils import timezone
        queryset.update(admin_validation='approved', status='pending', validated_by=request.user, validation_date=timezone.now())
    approve_proposals.short_description = "Approuver les propositions sélectionnées"
    
    def reject_proposals(self, request, queryset):
        from django.utils import timezone
        queryset.update(admin_validation='rejected', status='rejected', validated_by=request.user, validation_date=timezone.now())
    reject_proposals.short_description = "Rejeter les propositions sélectionnées"
    
    def feature_proposals(self, request, queryset):
        queryset.update(is_featured=True)
    feature_proposals.short_description = "Mettre en avant les propositions sélectionnées"
    
    def unfeature_proposals(self, request, queryset):
        queryset.update(is_featured=False)
    unfeature_proposals.short_description = "Retirer de la mise en avant"

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['project', 'client', 'freelancer', 'rating', 'is_public', 'created_at']
    list_filter = ['rating', 'is_public', 'created_at']
    search_fields = ['project__title', 'client__user__first_name', 'freelancer__user__first_name', 'comment']
    ordering = ['-rating', '-created_at']
    list_editable = ['is_public']
    actions = ['make_public', 'make_private']
    
    def make_public(self, request, queryset):
        queryset.update(is_public=True)
    make_public.short_description = "Rendre public les avis sélectionnés"
    
    def make_private(self, request, queryset):
        queryset.update(is_public=False)
    make_private.short_description = "Rendre privé les avis sélectionnés"

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'content_preview', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['content', 'sender__first_name', 'sender__last_name', 'receiver__first_name', 'receiver__last_name']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    actions = ['mark_as_read', 'mark_as_unread']
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Contenu'
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Marquer comme lu"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
    mark_as_unread.short_description = "Marquer comme non lu"

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'notification_type', 'title', 'is_read', 'is_important', 'created_at']
    list_filter = ['notification_type', 'is_read', 'is_important', 'created_at']
    search_fields = ['title', 'message', 'recipient__first_name', 'recipient__last_name']
    readonly_fields = ['recipient', 'notification_type', 'title', 'message', 'related_object_id', 'related_object_type', 'created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    list_editable = ['is_read', 'is_important']
    actions = ['mark_as_read', 'mark_as_unread', 'mark_as_important', 'mark_as_not_important']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Marquer comme lu"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
    mark_as_unread.short_description = "Marquer comme non lu"
    
    def mark_as_important(self, request, queryset):
        queryset.update(is_important=True)
    mark_as_important.short_description = "Marquer comme important"
    
    def mark_as_not_important(self, request, queryset):
        queryset.update(is_important=False)
    mark_as_not_important.short_description = "Marquer comme non important"

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['project', 'client', 'freelancer', 'amount', 'payment_method', 'status', 'transaction_id', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['transaction_id', 'description', 'project__title']
    readonly_fields = ['project', 'client', 'freelancer', 'amount', 'payment_method', 'status', 'transaction_id', 'description', 'created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    actions = ['mark_as_completed', 'mark_as_failed', 'mark_as_refunded']
    
    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_as_completed.short_description = "Marquer comme terminé"
    
    def mark_as_failed(self, request, queryset):
        queryset.update(status='failed')
    mark_as_failed.short_description = "Marquer comme échoué"
    
    def mark_as_refunded(self, request, queryset):
        queryset.update(status='refunded')
    mark_as_refunded.short_description = "Marquer comme remboursé"

@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ['project', 'title', 'due_date', 'amount', 'status', 'created_at']
    list_filter = ['status', 'due_date', 'created_at']
    search_fields = ['title', 'description', 'project__title']
    date_hierarchy = 'created_at'
    ordering = ['due_date']
    list_editable = ['status']
    actions = ['mark_as_completed', 'mark_as_approved', 'mark_as_rejected']
    
    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_as_completed.short_description = "Marquer comme terminé"
    
    def mark_as_approved(self, request, queryset):
        queryset.update(status='approved')
    mark_as_approved.short_description = "Marquer comme approuvé"
    
    def mark_as_rejected(self, request, queryset):
        queryset.update(status='rejected')
    mark_as_rejected.short_description = "Marquer comme rejeté"

@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = ['project', 'initiator', 'reason', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['reason', 'description', 'project__title', 'initiator__first_name', 'initiator__last_name']
    readonly_fields = ['project', 'initiator', 'reason', 'description', 'evidence', 'created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    list_editable = ['status']
    actions = ['mark_as_resolved', 'mark_as_closed']
    
    def mark_as_resolved(self, request, queryset):
        queryset.update(status='resolved')
    mark_as_resolved.short_description = "Marquer comme résolu"
    
    def mark_as_closed(self, request, queryset):
        queryset.update(status='closed')
    mark_as_closed.short_description = "Marquer comme fermé"

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'subject', 'ticket_type', 'priority', 'status', 'assigned_to', 'created_at']
    list_filter = ['status', 'priority', 'ticket_type', 'created_at']
    search_fields = ['subject', 'description', 'user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    ordering = ['-priority', '-created_at']
    list_editable = ['status', 'assigned_to']
    actions = ['mark_in_progress', 'mark_resolved', 'mark_closed', 'assign_to_me']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('user', 'subject', 'description', 'ticket_type', 'priority')
        }),
        ('Statut et assignation', {
            'fields': ('status', 'assigned_to', 'related_project')
        }),
        ('Résolution', {
            'fields': ('resolution',),
            'classes': ('collapse',)
        }),
        ('Fichiers', {
            'fields': ('attachments',),
            'classes': ('collapse',)
        })
    )
    
    def mark_in_progress(self, request, queryset):
        queryset.update(status='in_progress', assigned_to=request.user)
    mark_in_progress.short_description = "Marquer comme en cours de traitement"
    
    def mark_resolved(self, request, queryset):
        queryset.update(status='resolved')
    mark_resolved.short_description = "Marquer comme résolu"
    
    def mark_closed(self, request, queryset):
        queryset.update(status='closed')
    mark_closed.short_description = "Marquer comme fermé"
    
    def assign_to_me(self, request, queryset):
        queryset.update(assigned_to=request.user)
    assign_to_me.short_description = "S'assigner les tickets sélectionnés"

@admin.register(TicketResponse)
class TicketResponseAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'user', 'message_preview', 'is_staff_response', 'created_at']
    list_filter = ['is_staff_response', 'created_at']
    search_fields = ['message', 'user__first_name', 'user__last_name', 'ticket__subject']
    readonly_fields = ['created_at']
    ordering = ['ticket', 'created_at']
    
    def message_preview(self, obj):
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'

# Modèles de paiement
@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'payment_type', 'is_available', 'status', 'processing_fee', 'min_amount']
    list_filter = ['payment_type', 'is_available', 'status', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_available', 'status']
    ordering = ['name']

@admin.register(PaymentGateway)
class PaymentGatewayAdmin(admin.ModelAdmin):
    list_display = ['name', 'gateway_type', 'is_active', 'status', 'processing_fee', 'fixed_fee']
    list_filter = ['gateway_type', 'is_active', 'status', 'created_at']
    search_fields = ['name']
    list_editable = ['is_active', 'status']
    ordering = ['name']

@admin.register(CryptoPayment)
class CryptoPaymentAdmin(admin.ModelAdmin):
    list_display = ['payment', 'crypto_type', 'crypto_amount', 'exchange_rate', 'status', 'created_at']
    list_filter = ['crypto_type', 'status', 'created_at']
    search_fields = ['payment__transaction_id', 'wallet_address']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

@admin.register(MobileMoneyPayment)
class MobileMoneyPaymentAdmin(admin.ModelAdmin):
    list_display = ['payment', 'provider', 'phone_number', 'status', 'created_at']
    list_filter = ['provider', 'status', 'created_at']
    search_fields = ['payment__transaction_id', 'phone_number']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

@admin.register(PayPalPayment)
class PayPalPaymentAdmin(admin.ModelAdmin):
    list_display = ['payment', 'paypal_order_id', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['payment__transaction_id', 'paypal_order_id']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'payment', 'transaction_type', 'amount', 'currency', 'status', 'created_at']
    list_filter = ['transaction_type', 'status', 'currency', 'created_at']
    search_fields = ['transaction_id', 'payment__transaction_id']
    readonly_fields = ['transaction_id', 'created_at', 'updated_at']
    ordering = ['-created_at']

# Configuration de l'interface d'administration
admin.site.site_header = "Administration FreeAfrique"
admin.site.site_title = "FreeAfrique Admin"
admin.site.index_title = "Tableau de bord FreeAfrique"
