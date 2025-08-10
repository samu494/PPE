from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Count, Avg, Sum
from django.utils import timezone
from datetime import timedelta
from .models import (
    Freelancer, Client, Project, Proposal, Review, 
    Message, Notification, Payment, SupportTicket, 
    Category, Skill
)

@staff_member_required
def admin_dashboard(request):
    """Tableau de bord personnalisé pour l'administration"""
    
    # Statistiques générales
    total_freelancers = Freelancer.objects.count()
    total_clients = Client.objects.count()
    total_projects = Project.objects.count()
    total_proposals = Proposal.objects.count()
    
    # Statistiques des 30 derniers jours
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    new_freelancers = Freelancer.objects.filter(created_at__gte=thirty_days_ago).count()
    new_clients = Client.objects.filter(created_at__gte=thirty_days_ago).count()
    new_projects = Project.objects.filter(created_at__gte=thirty_days_ago).count()
    new_proposals = Proposal.objects.filter(created_at__gte=thirty_days_ago).count()
    
    # Projets par statut
    projects_by_status = Project.objects.values('status').annotate(count=Count('id'))
    
    # Propositions en attente de validation
    pending_proposals = Proposal.objects.filter(admin_validation='pending').count()
    approved_proposals = Proposal.objects.filter(admin_validation='approved').count()
    rejected_proposals = Proposal.objects.filter(admin_validation='rejected').count()
    
    # Tickets de support
    open_tickets = SupportTicket.objects.filter(status='open').count()
    in_progress_tickets = SupportTicket.objects.filter(status='in_progress').count()
    resolved_tickets = SupportTicket.objects.filter(status='resolved').count()
    
    # Top catégories
    top_categories = Category.objects.annotate(
        project_count=Count('project'),
        freelancer_count=Count('freelancer')
    ).order_by('-project_count')[:5]
    
    # Top freelances
    top_freelancers = Freelancer.objects.filter(rating__gt=0).order_by('-rating')[:5]
    
    # Statistiques financières
    total_earnings = Freelancer.objects.aggregate(total=Sum('total_earnings'))['total'] or 0
    total_spent = Client.objects.aggregate(total=Sum('total_spent'))['total'] or 0
    
    # Messages et notifications
    unread_messages = Message.objects.filter(is_read=False).count()
    unread_notifications = Notification.objects.filter(is_read=False).count()
    
    context = {
        'total_freelancers': total_freelancers,
        'total_clients': total_clients,
        'total_projects': total_projects,
        'total_proposals': total_proposals,
        'new_freelancers': new_freelancers,
        'new_clients': new_clients,
        'new_projects': new_projects,
        'new_proposals': new_proposals,
        'projects_by_status': projects_by_status,
        'pending_proposals': pending_proposals,
        'approved_proposals': approved_proposals,
        'rejected_proposals': rejected_proposals,
        'open_tickets': open_tickets,
        'in_progress_tickets': in_progress_tickets,
        'resolved_tickets': resolved_tickets,
        'top_categories': top_categories,
        'top_freelancers': top_freelancers,
        'total_earnings': total_earnings,
        'total_spent': total_spent,
        'unread_messages': unread_messages,
        'unread_notifications': unread_notifications,
    }
    
    return render(request, 'admin/dashboard.html', context)

@staff_member_required
def admin_statistics(request):
    """Page de statistiques détaillées"""
    
    # Statistiques par mois (6 derniers mois)
    months = []
    freelancer_counts = []
    client_counts = []
    project_counts = []
    
    for i in range(6):
        month_start = timezone.now() - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        
        months.append(month_start.strftime('%B %Y'))
        freelancer_counts.append(
            Freelancer.objects.filter(created_at__gte=month_start, created_at__lt=month_end).count()
        )
        client_counts.append(
            Client.objects.filter(created_at__gte=month_start, created_at__lt=month_end).count()
        )
        project_counts.append(
            Project.objects.filter(created_at__gte=month_start, created_at__lt=month_end).count()
        )
    
    # Statistiques des catégories
    category_stats = Category.objects.annotate(
        project_count=Count('project'),
        freelancer_count=Count('freelancer'),
        avg_rating=Avg('freelancer__rating')
    ).order_by('-project_count')
    
    # Statistiques des paiements
    payment_stats = Payment.objects.values('status').annotate(
        count=Count('id'),
        total_amount=Sum('amount')
    )
    
    # Statistiques des avis
    review_stats = Review.objects.values('rating').annotate(
        count=Count('id')
    ).order_by('rating')
    
    context = {
        'months': months,
        'freelancer_counts': freelancer_counts,
        'client_counts': client_counts,
        'project_counts': project_counts,
        'category_stats': category_stats,
        'payment_stats': payment_stats,
        'review_stats': review_stats,
    }
    
    return render(request, 'admin/statistics.html', context)

