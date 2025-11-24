from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q, Avg, Count, Sum, F, Min, Max
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.cache import cache
from django.db.models.functions import Coalesce
from datetime import datetime, timedelta
import json
import math
from .models import *
from .forms import *
from django.db import models
import sys
from django.conf import settings
import uuid

def how_it_works(request):
    """Page expliquant le fonctionnement de la plateforme"""
    return render(request, 'how_it_works.html')

def role_selection(request):
    """Page de sélection de rôle pour connexion/inscription"""
    return render(request, 'role_selection.html')

def first_time_guide(request):
    """Guide pour les nouveaux utilisateurs"""
    return render(request, 'first_time_guide.html')

def home(request):
    """Page d'accueil avec statistiques en temps réel et recommandations"""
    
    # Statistiques en temps réel
    stats = cache.get('home_stats')
    if not stats:
        stats = {
            'total_freelancers': Freelancer.objects.count(),
            'total_clients': Client.objects.count(),
            'total_projects': Project.objects.count(),
            'total_earnings': Freelancer.objects.aggregate(
                total=Coalesce(Sum('total_earnings'), 0, output_field=models.DecimalField())
            )['total'],
            'completed_projects': Project.objects.filter(status='completed').count(),
            'active_projects': Project.objects.filter(status='open').count(),
        }
        cache.set('home_stats', stats, 300)  # Cache pour 5 minutes
    
    # Catégories populaires
    categories = Category.objects.filter(is_featured=True)[:6]
    
    # Freelances vedettes
    featured_freelancers = Freelancer.objects.filter(
        is_featured=True, 
        availability_status='available'
    ).order_by('-rating')[:8]
    
    # Projets récents et urgents
    recent_projects = Project.objects.filter(
        status='open'
    ).order_by('-is_urgent', '-created_at')[:6]
    
    # Projets recommandés pour l'utilisateur connecté
    recommended_projects = []
    if request.user.is_authenticated:
        try:
            freelancer = Freelancer.objects.get(user=request.user)
            # Projets correspondant aux compétences du freelance
            user_skills = freelancer.skills or []
            if user_skills:
                recommended_projects = Project.objects.filter(
                    status='open'
                ).exclude(
                    proposals__freelancer=freelancer
                ).order_by('-is_urgent', '-created_at')[:4]
        except Freelancer.DoesNotExist:
            pass
    
    # Statistiques des gains par catégorie
    category_stats = cache.get('category_stats')
    if not category_stats:
        category_stats = Category.objects.annotate(
            avg_earnings=Avg('project__proposal__price'),
            project_count_annot=Count('project')
        ).order_by('-project_count_annot')[:8]
        cache.set('category_stats', category_stats, 600)
    
    context = {
        'stats': stats,
        'categories': categories,
        'featured_freelancers': featured_freelancers,
        'recent_projects': recent_projects,
        'recommended_projects': recommended_projects,
        'category_stats': category_stats,
    }
    
    return render(request, 'home.html', context)

def search(request):
    """Recherche avancée avec filtres intelligents"""
    query = request.GET.get('q', '')
    search_type = request.GET.get('type', 'all')  # all, projects, freelancers
    category_id = request.GET.get('category', '')
    budget_min = request.GET.get('budget_min', '')
    budget_max = request.GET.get('budget_max', '')
    skills = request.GET.getlist('skills', [])
    rating_min = request.GET.get('rating_min', '')
    location = request.GET.get('location', '')
    sort_by = request.GET.get('sort', 'relevance')
    
    projects = []
    freelancers = []
    
    if search_type in ['all', 'projects']:
        projects = Project.objects.filter(status='open')
        
        if query:
            projects = projects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query)
            )
        
        if category_id:
            projects = projects.filter(category_id=category_id)
        
        if budget_min:
            projects = projects.filter(budget_max__gte=float(budget_min))
        
        if budget_max:
            projects = projects.filter(budget_min__lte=float(budget_max))
        
        if skills:
            # Filtrer les projets qui ont au moins une des compétences requises
            for skill in skills:
                projects = projects.filter(required_skills__contains=[skill])
        
        # Tri
        if sort_by == 'budget_high':
            projects = projects.order_by('-budget_max')
        elif sort_by == 'budget_low':
            projects = projects.order_by('budget_min')
        elif sort_by == 'recent':
            projects = projects.order_by('-created_at')
        elif sort_by == 'urgent':
            projects = projects.order_by('-is_urgent', '-created_at')
        else:  # relevance
            projects = projects.order_by('-is_featured', '-views_count', '-created_at')
    
    if search_type in ['all', 'freelancers']:
        freelancers = Freelancer.objects.filter(availability_status='available')
        
        if query:
            freelancers = freelancers.filter(
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(description__icontains=query)
            )
        
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                is_sqlite = settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3'
                if is_sqlite:
                    # Stocker les IDs des freelancers qui correspondent au critère
                    matching_freelancer_ids = [f.id for f in freelancers if category.name in (f.skills or [])]
                    # Filtrer à nouveau à partir de la base de données pour conserver un QuerySet
                    freelancers = Freelancer.objects.filter(id__in=matching_freelancer_ids)
                else:
                    freelancers = freelancers.filter(skills__contains=[category.name])
            except Category.DoesNotExist:
                pass
        
        if rating_min:
            freelancers = freelancers.filter(rating__gte=float(rating_min))
        
        rate_min = request.GET.get('rate_min', '')
        rate_max = request.GET.get('rate_max', '')
        
        if rate_min:
            freelancers = freelancers.filter(hourly_rate__gte=float(rate_min))
        
        if rate_max:
            freelancers = freelancers.filter(hourly_rate__lte=float(rate_max))
        
        if location:
            freelancers = freelancers.filter(location__icontains=location)
        
        availability = request.GET.get('availability', '')
        if availability:
            freelancers = freelancers.filter(availability_status=availability)
        
        if skills:
            # Filtrer les freelances qui ont au moins une des compétences
            is_sqlite = settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3'
            if is_sqlite:
                # Pour SQLite, nous devons filtrer manuellement
                # Récupérer tous les freelancers pour filtrage manuel
                all_freelancers = list(freelancers)
                filtered_freelancers = []
                for f in all_freelancers:
                    has_skill = False
                    for skill in skills:
                        if f.skills and skill in f.skills:
                            has_skill = True
                            break
                    if has_skill:
                        filtered_freelancers.append(f)
                # Convertir la liste filtrée en QuerySet
                freelancer_ids = [f.id for f in filtered_freelancers]
                freelancers = Freelancer.objects.filter(id__in=freelancer_ids)
            else:
                # Pour les autres bases de données qui supportent contains
                for skill in skills:
                    freelancers = freelancers.filter(skills__contains=[skill])
        
        # Tri
        if sort_by == 'rating':
            freelancers = freelancers.order_by('-rating')
        elif sort_by == 'rate_high':
            freelancers = freelancers.order_by('-hourly_rate')
        elif sort_by == 'rate_low':
            freelancers = freelancers.order_by('hourly_rate')
        elif sort_by == 'experience':
            freelancers = freelancers.order_by('-experience_years')
        else:  # relevance
            freelancers = freelancers.order_by('-is_featured', '-rating', '-completed_projects')
    
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(projects, 12)
    projects_page = paginator.get_page(page)
    
    paginator_freelancers = Paginator(freelancers, 12)
    freelancers_page = paginator_freelancers.get_page(page)
    
    # Suggestions de recherche
    suggestions = []
    if query and len(query) > 2:
        # Projets similaires
        similar_projects = Project.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        ).values_list('title', flat=True)[:5]
        
        # Compétences populaires
        popular_skills = Skill.objects.filter(
            name__icontains=query
        ).values_list('name', flat=True)[:5]
        
        suggestions = list(similar_projects) + list(popular_skills)
    
    context = {
        'query': query,
        'search_type': search_type,
        'projects': projects_page,
        'freelancers': freelancers_page,
        'suggestions': suggestions,
        'categories': Category.objects.all(),
        'skills': Skill.objects.filter(is_popular=True),
        'filters': {
            'category_id': category_id,
            'budget_min': budget_min,
            'budget_max': budget_max,
            'skills': skills,
            'rating_min': rating_min,
            'location': location,
            'sort_by': sort_by,
        }
    }
    
    return render(request, 'search.html', context)

@login_required
def dashboard(request):
    """Tableau de bord personnalisé avec statistiques avancées"""
    user = request.user
    
    # Vérifier si c'est la première connexion de l'utilisateur
    if not hasattr(user, 'freelancer') and not hasattr(user, 'client'):
        # Rediriger vers le guide pour les nouveaux utilisateurs
        return redirect('first_time_guide')
    
    try:
        unread_notifications = Notification.objects.filter(recipient=user, is_read=False).count()
        recent_conversations = []
        # Construire les conversations récentes (max 5)
        participants = set()
        recent_messages = Message.objects.filter(Q(sender=user) | Q(receiver=user)).order_by('-created_at')[:50]
        for msg in recent_messages:
            other_user = msg.receiver if msg.sender == user else msg.sender
            if other_user.id in participants:
                continue
            unread_count = Message.objects.filter(sender=other_user, receiver=user, is_read=False).count()
            recent_conversations.append({
                'id': other_user.id,
                'other_user': other_user,
                'last_message': msg.content,
                'last_message_time': msg.created_at,
                'unread_count': unread_count,
            })
            participants.add(other_user.id)
            if len(recent_conversations) >= 5:
                break
        
        if hasattr(user, 'freelancer'):
            # Dashboard Freelance
            freelancer = user.freelancer
            
            # Statistiques du mois
            current_month = timezone.now().month
            current_year = timezone.now().year
            
            monthly_stats = {
                'proposals_sent': Proposal.objects.filter(
                    freelancer=freelancer,
                    created_at__month=current_month,
                    created_at__year=current_year
                ).count(),
                'proposals_accepted': Proposal.objects.filter(
                    freelancer=freelancer,
                    status='accepted',
                    created_at__month=current_month,
                    created_at__year=current_year
                ).count(),
                'earnings': Payment.objects.filter(
                    freelancer=freelancer,
                    status='completed',
                    created_at__month=current_month,
                    created_at__year=current_year
                ).aggregate(total=Coalesce(Sum('amount'), 0, output_field=models.DecimalField()))['total'],
                'active_projects': Project.objects.filter(
                    selected_freelancer=freelancer,
                    status='in_progress'
                ).count(),
            }
            
            # Projets actifs
            active_projects = Project.objects.filter(
                selected_freelancer=freelancer,
                status__in=['in_progress', 'open']
            ).order_by('-created_at')[:5]
            
            # Propositions récentes
            recent_proposals = Proposal.objects.filter(
                freelancer=freelancer
            ).order_by('-created_at')[:5]
            
            # Messages non lus
            unread_messages = Message.objects.filter(
                receiver=user,
                is_read=False
            ).count()
            
            # Graphique des gains (6 derniers mois)
            earnings_data = []
            for i in range(6):
                month = timezone.now() - timedelta(days=30*i)
                month_earnings = Payment.objects.filter(
                    freelancer=freelancer,
                    status='completed',
                    created_at__month=month.month,
                    created_at__year=month.year
                ).aggregate(total=Coalesce(Sum('amount'), 0, output_field=models.DecimalField()))['total']
                earnings_data.append({
                    'month': month.strftime('%B'),
                    'earnings': float(month_earnings)
                })
            
            # Projets récents/recommandés
            recent_projects = Project.objects.filter(status__in=['open', 'in_progress']).order_by('-is_urgent', '-created_at')[:6]
            
            # Variables attendues par le template
            context = {
                'user_type': 'freelancer',
                'monthly_stats': monthly_stats,
                'active_projects': active_projects,
                'recent_proposals': recent_proposals,
                'unread_messages': unread_messages,
                'unread_notifications': unread_notifications,
                'earnings_data': earnings_data,
                'freelancer': freelancer,
                'average_rating': freelancer.rating,
                'completed_projects': Project.objects.filter(selected_freelancer=freelancer, status='completed').count(),
                'recent_conversations': recent_conversations,
                'recent_projects': recent_projects,
            }
        elif hasattr(user, 'client'):
            # Dashboard Client
            client = user.client
            
            # Statistiques du mois
            current_month = timezone.now().month
            current_year = timezone.now().year
            
            monthly_stats = {
                'projects_created': Project.objects.filter(
                    client=client,
                    created_at__month=current_month,
                    created_at__year=current_year
                ).count(),
                'projects_completed': Project.objects.filter(
                    client=client,
                    status='completed',
                    created_at__month=current_month,
                    created_at__year=current_year
                ).count(),
                'total_spent': Payment.objects.filter(
                    client=client,
                    status='completed',
                    created_at__month=current_month,
                    created_at__year=current_year
                ).aggregate(total=Coalesce(Sum('amount'), 0, output_field=models.DecimalField()))['total'],
                'active_projects': Project.objects.filter(
                    client=client,
                    status__in=['open', 'in_progress']
                ).count(),
            }
            
            # Projets actifs / récents
            active_projects = Project.objects.filter(
                client=client,
                status__in=['open', 'in_progress']
            ).order_by('-created_at')[:5]
            recent_projects = Project.objects.filter(client=client).order_by('-created_at')[:6]
            
            # Propositions récentes
            recent_proposals = Proposal.objects.filter(
                project__client=client
            ).order_by('-created_at')[:5]
            
            # Messages non lus
            unread_messages = Message.objects.filter(
                receiver=user,
                is_read=False
            ).count()
            
            # Paiements en attente
            pending_payments = Payment.objects.filter(client=client, status='pending').select_related('project', 'freelancer')[:10]
            
            context = {
                'user_type': 'client',
                'monthly_stats': monthly_stats,
                'active_projects': active_projects,
                'recent_proposals': recent_proposals,
                'unread_messages': unread_messages,
                'unread_notifications': unread_notifications,
                'client': client,
                'recent_conversations': recent_conversations,
                'pending_payments': pending_payments,
                'total_proposals': Proposal.objects.filter(project__client=client).count(),
                'recent_projects': recent_projects,
            }
        else:
            # Utilisateur sans profil complet
            messages.warning(request, "Veuillez compléter votre profil pour accéder au tableau de bord.")
            return redirect('complete_profile')
        
    except Exception as e:
        messages.error(request, f"Erreur lors du chargement du tableau de bord: {str(e)}")
        return redirect('home')
    
    return render(request, 'dashboard.html', context)

@login_required
def projects_list(request):
    """Liste des projets avec filtres avancés et recommandations"""
    
    # Filtres
    category_id = request.GET.get('category', '')
    budget_min = request.GET.get('budget_min', '')
    budget_max = request.GET.get('budget_max', '')
    skills = request.GET.getlist('skills', [])
    status = request.GET.get('status', 'open')
    sort_by = request.GET.get('sort', 'recent')
    
    projects = Project.objects.all()
    
    # Filtre par statut
    if status:
        projects = projects.filter(status=status)
    
    # Filtre par catégorie
    if category_id:
        projects = projects.filter(category_id=category_id)
    
    # Filtre par budget
    if budget_min:
        projects = projects.filter(budget_max__gte=float(budget_min))
    if budget_max:
        projects = projects.filter(budget_min__lte=float(budget_max))
    
    # Filtre par compétences
    if skills:
        # Filtrer les projets qui ont au moins une des compétences requises
        for skill in skills:
            projects = projects.filter(required_skills__contains=[skill])
    
    # Tri
    if sort_by == 'budget_high':
        projects = projects.order_by('-budget_max')
    elif sort_by == 'budget_low':
        projects = projects.order_by('budget_min')
    elif sort_by == 'deadline':
        projects = projects.order_by('deadline')
    elif sort_by == 'popular':
        projects = projects.order_by('-views_count', '-proposals_count')
    else:  # recent
        projects = projects.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(projects, 12)
    page = request.GET.get('page', 1)
    projects_page = paginator.get_page(page)
    
    # Statistiques
    stats = {
        'total_projects': Project.objects.count(),
        'open_projects': Project.objects.filter(status='open').count(),
        'total_budget': Project.objects.filter(status='open').aggregate(
            total=Coalesce(Sum('budget_max'), 0, output_field=models.DecimalField())
        )['total'],
        'avg_budget': Project.objects.filter(status='open').aggregate(
            avg=Coalesce(Avg('budget_max'), 0, output_field=models.DecimalField())
        )['avg'],
    }
    
    # Projets recommandés pour l'utilisateur connecté
    recommended_projects = []
    if request.user.is_authenticated:
        try:
            freelancer = Freelancer.objects.get(user=request.user)
            user_skills = freelancer.skills or []
            if user_skills:
                recommended_projects = Project.objects.filter(
                    status='open'
                ).exclude(
                    proposals__freelancer=freelancer
                ).order_by('-is_urgent', '-created_at')[:3]
        except Freelancer.DoesNotExist:
            pass
    
    context = {
        'projects': projects_page,
        'stats': stats,
        'recommended_projects': recommended_projects,
        'categories': Category.objects.all(),
        'skills': Skill.objects.filter(is_popular=True),
        'filters': {
            'category_id': category_id,
            'budget_min': budget_min,
            'budget_max': budget_max,
            'skills': skills,
            'status': status,
            'sort_by': sort_by,
        }
    }
    
    return render(request, 'projects_list.html', context)

@login_required
def project_detail(request, project_id):
    """Détail du projet avec analyses et recommandations"""
    project = get_object_or_404(Project, id=project_id)
    
    # Incrémenter le compteur de vues
    project.views_count += 1
    project.save()
    
    # Vérifier si l'utilisateur a déjà proposé
    user_proposal = None
    if request.user.is_authenticated:
        try:
            freelancer = Freelancer.objects.get(user=request.user)
            user_proposal = Proposal.objects.filter(
                project=project,
                freelancer=freelancer
            ).first()
        except Freelancer.DoesNotExist:
            pass
    
    # Propositions reçues
    proposals = Proposal.objects.filter(project=project).order_by('-is_featured', '-created_at')
    
    # Statistiques du projet
    project_stats = {
        'total_proposals': proposals.count(),
        'avg_proposal_price': proposals.aggregate(avg=Coalesce(Avg('price'), 0, output_field=models.DecimalField()))['avg'],
        'min_proposal_price': proposals.aggregate(min=Coalesce(Min('price'), 0, output_field=models.DecimalField()))['min'],
        'max_proposal_price': proposals.aggregate(max=Coalesce(Max('price'), 0, output_field=models.DecimalField()))['max'],
        'days_remaining': (project.deadline - timezone.now().date()).days,
    }
    
    # Freelances recommandés pour ce projet
    recommended_freelancers = []
    if project.required_skills:
        for skill in project.required_skills:
            recommended_freelancers = Freelancer.objects.filter(
                skills__contains=[skill],
                availability_status='available'
            ).exclude(
                proposals__project=project
            ).order_by('-rating', '-completed_projects')[:5]
            if recommended_freelancers:
                break
    
    # Projets similaires
    similar_projects = Project.objects.filter(
        category=project.category,
        status='open'
    ).exclude(id=project.id).order_by('-created_at')[:3]
    
    context = {
        'project': project,
        'proposals': proposals,
        'user_proposal': user_proposal,
        'project_stats': project_stats,
        'recommended_freelancers': recommended_freelancers,
        'similar_projects': similar_projects,
    }
    
    return render(request, 'project_detail.html', context)

@login_required
def create_project(request):
    """Création de projet avec assistant intelligent"""
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.client = request.user.client
            project.save()
            
            # Créer une notification pour les freelances correspondants
            freelancers = Freelancer.objects.filter(
                availability_status='available'
            )
            
            # Filtrer les freelances qui ont les compétences requises
            if project.required_skills:
                for skill in project.required_skills:
                    freelancers = freelancers.filter(skills__contains=[skill])
            
            for freelancer in freelancers[:50]:  # Limiter à 50 notifications
                Notification.objects.create(
                    recipient=freelancer.user,
                    notification_type='project_proposal',
                    title=f"Nouveau projet dans votre domaine",
                    message=f"Un nouveau projet '{project.title}' correspond à vos compétences.",
                    related_object_id=project.id,
                    related_object_type='project'
                )
            
            messages.success(request, "Projet créé avec succès !")
            return redirect('project_detail', project_id=project.id)
    else:
        form = ProjectForm()
    
    # Suggestions de budget basées sur la catégorie
    budget_suggestions = {
        'Développement Web': {'min': 500, 'max': 5000},
        'Design Graphique': {'min': 200, 'max': 2000},
        'Rédaction': {'min': 100, 'max': 1000},
        'Marketing Digital': {'min': 300, 'max': 3000},
    }
    
    context = {
        'form': form,
        'budget_suggestions': budget_suggestions,
        'categories': Category.objects.all(),
        'skills': Skill.objects.all(),
    }
    
    return render(request, 'create_project.html', context)

@login_required
def submit_proposal(request, project_id):
    """Soumission de proposition avec analyse de marché"""
    project = get_object_or_404(Project, id=project_id)
    
    # Vérifier que l'utilisateur est un freelance
    try:
        freelancer = Freelancer.objects.get(user=request.user)
    except Freelancer.DoesNotExist:
        messages.error(request, "Seuls les freelances peuvent soumettre des propositions.")
        return redirect('project_detail', project_id=project_id)
    
    # Vérifier si l'utilisateur a déjà proposé
    existing_proposal = Proposal.objects.filter(
        project=project,
        freelancer=freelancer
    ).first()
    
    if existing_proposal:
        messages.warning(request, "Vous avez déjà soumis une proposition pour ce projet.")
        return redirect('project_detail', project_id=project_id)
    
    if request.method == 'POST':
        form = ProposalForm(request.POST, request.FILES)
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.project = project
            proposal.freelancer = freelancer
            proposal.save()
            
            # Mettre à jour le compteur de propositions
            project.proposals_count += 1
            project.save()
            
            # Créer une notification pour le client
            Notification.objects.create(
                recipient=project.client.user,
                notification_type='project_proposal',
                title=f"Nouvelle proposition reçue",
                message=f"Vous avez reçu une nouvelle proposition pour '{project.title}'.",
                related_object_id=proposal.id,
                related_object_type='proposal'
            )
            
            messages.success(request, "Proposition soumise avec succès !")
            return redirect('project_detail', project_id=project_id)
    else:
        form = ProposalForm()
    
    # Analyse de marché pour ce projet
    market_analysis = {
        'avg_proposal_price': Proposal.objects.filter(
            project__category=project.category
        ).aggregate(avg=Coalesce(Avg('price'), 0, output_field=models.DecimalField()))['avg'],
        'total_proposals': project.proposals_count,
        'avg_delivery_time': Proposal.objects.filter(
            project__category=project.category
        ).aggregate(avg=Coalesce(Avg('delivery_time'), 0, output_field=models.IntegerField()))['avg'],
    }
    
    context = {
        'project': project,
        'form': form,
        'market_analysis': market_analysis,
        'freelancer': freelancer,
    }
    
    return render(request, 'submit_proposal.html', context)

@login_required
def freelancers_list(request):
    """Liste des freelances avec filtres avancés et recommandations"""
    
    # Filtres
    skills = request.GET.getlist('skills', [])
    rating_min = request.GET.get('rating_min', '')
    rate_min = request.GET.get('rate_min', '')
    rate_max = request.GET.get('rate_max', '')
    location = request.GET.get('location', '')
    availability = request.GET.get('availability', '')
    sort_by = request.GET.get('sort', 'rating')
    
    freelancers = Freelancer.objects.all()
    
    # Filtre par compétences
    if skills:
        is_sqlite = settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3'
        if is_sqlite:
            for skill in skills:
                freelancers = [f for f in freelancers if skill in (f.skills or [])]
        else:
            for skill in skills:
                freelancers = freelancers.filter(skills__contains=[skill])
    
    # Filtre par note
    if rating_min:
        freelancers = freelancers.filter(rating__gte=float(rating_min))
    
    # Filtre par taux horaire
    if rate_min:
        freelancers = freelancers.filter(hourly_rate__gte=float(rate_min))
    if rate_max:
        freelancers = freelancers.filter(hourly_rate__lte=float(rate_max))
    
    # Filtre par localisation
    if location:
        freelancers = freelancers.filter(location__icontains=location)
    
    # Filtre par disponibilité
    if availability:
        freelancers = freelancers.filter(availability_status=availability)
    
    # Tri
    if isinstance(freelancers, list):
        if sort_by == 'rate_high':
            freelancers = sorted(freelancers, key=lambda f: f.hourly_rate, reverse=True)
        elif sort_by == 'rate_low':
            freelancers = sorted(freelancers, key=lambda f: f.hourly_rate)
        elif sort_by == 'experience':
            freelancers = sorted(freelancers, key=lambda f: f.experience_years, reverse=True)
        elif sort_by == 'projects':
            freelancers = sorted(freelancers, key=lambda f: f.completed_projects, reverse=True)
        elif sort_by == 'earnings':
            freelancers = sorted(freelancers, key=lambda f: f.total_earnings, reverse=True)
        else:  # rating
            freelancers = sorted(freelancers, key=lambda f: (f.rating, f.total_reviews), reverse=True)
    else:
        if sort_by == 'rate_high':
            freelancers = freelancers.order_by('-hourly_rate')
        elif sort_by == 'rate_low':
            freelancers = freelancers.order_by('hourly_rate')
        elif sort_by == 'experience':
            freelancers = freelancers.order_by('-experience_years')
        elif sort_by == 'projects':
            freelancers = freelancers.order_by('-completed_projects')
        elif sort_by == 'earnings':
            freelancers = freelancers.order_by('-total_earnings')
        else:  # rating
            freelancers = freelancers.order_by('-rating', '-total_reviews')
    
    # Pagination
    paginator = Paginator(freelancers, 12)
    page = request.GET.get('page', 1)
    freelancers_page = paginator.get_page(page)
    
    # Statistiques
    stats = {
        'total_freelancers': Freelancer.objects.count(),
        'avg_rating': Freelancer.objects.aggregate(avg=Coalesce(Avg('rating'), 0, output_field=models.DecimalField()))['avg'],
        'avg_hourly_rate': Freelancer.objects.aggregate(avg=Coalesce(Avg('hourly_rate'), 0, output_field=models.DecimalField()))['avg'],
        'total_earnings': Freelancer.objects.aggregate(total=Coalesce(Sum('total_earnings'), 0, output_field=models.DecimalField()))['total'],
    }
    
    # Freelances recommandés basés sur les projets actifs
    recommended_freelancers = []
    if request.user.is_authenticated:
        try:
            client = Client.objects.get(user=request.user)
            active_projects = Project.objects.filter(client=client, status='open')
            if active_projects.exists():
                project_skills = []
                for project in active_projects:
                    if project.required_skills:
                        project_skills.extend(project.required_skills)
                
                if project_skills:
                    for skill in project_skills:
                        recommended_freelancers = Freelancer.objects.filter(
                            skills__contains=[skill],
                            availability_status='available'
                        ).order_by('-rating')[:5]
                        if recommended_freelancers:
                            break
        except Client.DoesNotExist:
            pass
    
    context = {
        'freelancers': freelancers_page,
        'stats': stats,
        'recommended_freelancers': recommended_freelancers,
        'skills': Skill.objects.filter(is_popular=True),
        'filters': {
            'skills': skills,
            'rating_min': rating_min,
            'rate_min': rate_min,
            'rate_max': rate_max,
            'location': location,
            'availability': availability,
            'sort_by': sort_by,
        }
    }
    
    return render(request, 'freelancers_list.html', context)

@login_required
def freelancer_detail(request, freelancer_id):
    """Profil détaillé du freelance avec analyses"""
    freelancer = get_object_or_404(Freelancer, id=freelancer_id)
    
    # Projets récents
    recent_projects = Project.objects.filter(
        selected_freelancer=freelancer,
        status='completed'
    ).order_by('-updated_at')[:5]
    
    # Avis reçus
    reviews = Review.objects.filter(freelancer=freelancer).order_by('-created_at')
    
    # Statistiques détaillées
    stats = {
        'total_projects': Project.objects.filter(selected_freelancer=freelancer).count(),
        'completed_projects': Project.objects.filter(
            selected_freelancer=freelancer,
            status='completed'
        ).count(),
        'avg_project_rating': reviews.aggregate(avg=Coalesce(Avg('rating'), 0, output_field=models.FloatField()))['avg'],
        'on_time_delivery': reviews.filter(rating__gte=4).count(),
        'client_satisfaction': reviews.filter(rating__gte=4).count() / max(reviews.count(), 1) * 100,
    }
    
    # Graphique des gains par mois (12 derniers mois)
    earnings_by_month = []
    for i in range(12):
        month = timezone.now() - timedelta(days=30*i)
        month_earnings = Payment.objects.filter(
            freelancer=freelancer,
            status='completed',
            created_at__month=month.month,
            created_at__year=month.year
        ).aggregate(total=Coalesce(Sum('amount'), 0, output_field=models.DecimalField()))['total']
        earnings_by_month.append({
            'month': month.strftime('%B'),
            'earnings': float(month_earnings)
        })
    
    # Compétences avec niveau d'expertise
    skills_with_expertise = []
    for skill in freelancer.skills:
        # Calculer le niveau d'expertise basé sur les projets réussis
        is_sqlite = settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3'
        if is_sqlite:
            # Pour SQLite, filtrer manuellement
            skill_projects = 0
            for project in Project.objects.filter(selected_freelancer=freelancer, status='completed'):
                if skill in (project.required_skills or []):
                    skill_projects += 1
        else:
            skill_projects = Project.objects.filter(
                selected_freelancer=freelancer,
                required_skills__contains=[skill],
                status='completed'
            ).count()
        
        expertise_level = 'Débutant'
        if skill_projects > 10:
            expertise_level = 'Expert'
        elif skill_projects > 5:
            expertise_level = 'Intermédiaire'
        elif skill_projects > 2:
            expertise_level = 'Avancé'
        
        skills_with_expertise.append({
            'name': skill,
            'expertise': expertise_level,
            'projects_count': skill_projects
        })
    
    # Projets similaires disponibles
    similar_projects = []
    if freelancer.skills:
        is_sqlite = settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3'
        if is_sqlite:
            # Pour SQLite, filtrer manuellement
            for skill in freelancer.skills:
                # Récupérer les projets où le freelancer a déjà fait une proposition
                freelancer_proposal_projects = Proposal.objects.filter(freelancer=freelancer).values_list('project_id', flat=True)
                potential_projects = Project.objects.filter(status='open').exclude(id__in=freelancer_proposal_projects)
                matching_projects = []
                for project in potential_projects:
                    if skill in (project.required_skills or []):
                        matching_projects.append(project)
                if matching_projects:
                    # Trier manuellement
                    matching_projects.sort(key=lambda p: (-p.is_urgent, -p.created_at.timestamp()))
                    similar_projects = matching_projects[:3]
                    break
        else:
            for skill in freelancer.skills:
                # Récupérer les projets où le freelancer a déjà fait une proposition
                freelancer_proposal_projects = Proposal.objects.filter(freelancer=freelancer).values_list('project_id', flat=True)
                similar_projects = Project.objects.filter(
                    status='open',
                    required_skills__contains=[skill]
                ).exclude(
                    id__in=freelancer_proposal_projects
                ).order_by('-is_urgent', '-created_at')[:3]
                if similar_projects:
                    break
    
    context = {
        'freelancer': freelancer,
        'recent_projects': recent_projects,
        'reviews': reviews,
        'stats': stats,
        'earnings_by_month': earnings_by_month,
        'skills_with_expertise': skills_with_expertise,
        'similar_projects': similar_projects,
    }
    
    return render(request, 'freelancer_detail.html', context)

@login_required
def messages_list(request):
    """Liste des conversations avec indicateurs de statut"""
    user = request.user
    
    # Récupérer toutes les conversations
    conversations = []
    
    # Messages envoyés
    sent_conversations = Message.objects.filter(sender=user).values('receiver').distinct()
    for conv in sent_conversations:
        receiver = User.objects.get(id=conv['receiver'])
        last_message = Message.objects.filter(
            Q(sender=user, receiver=receiver) | Q(sender=receiver, receiver=user)
        ).order_by('-created_at').first()
        
        unread_count = Message.objects.filter(
            sender=receiver,
            receiver=user,
            is_read=False
        ).count()
        
        conversations.append({
            'other_user': receiver,
            'last_message': last_message,
            'unread_count': unread_count,
            'last_activity': last_message.created_at if last_message else None,
        })
    
    # Messages reçus (ajouter les conversations manquantes)
    received_conversations = Message.objects.filter(receiver=user).values('sender').distinct()
    for conv in received_conversations:
        sender = User.objects.get(id=conv['sender'])
        if not any(c['user'].id == sender.id for c in conversations):
            last_message = Message.objects.filter(
                Q(sender=user, receiver=sender) | Q(sender=sender, receiver=user)
            ).order_by('-created_at').first()
            
            unread_count = Message.objects.filter(
                sender=sender,
                receiver=user,
                is_read=False
            ).count()
            
            conversations.append({
                'other_user': sender,
                'last_message': last_message,
                'unread_count': unread_count,
                'last_activity': last_message.created_at if last_message else None,
            })
    
    # Trier par dernière activité
    conversations.sort(key=lambda x: x['last_activity'] or timezone.now(), reverse=True)
    
    context = {
        'conversations': conversations,
    }
    
    return render(request, 'messages_list.html', context)

@login_required
def conversation(request, user_id):
    """Conversation individuelle avec historique complet"""
    other_user = get_object_or_404(User, id=user_id)
    current_user = request.user
    
    # Marquer les messages comme lus
    Message.objects.filter(
        sender=other_user,
        receiver=current_user,
        is_read=False
    ).update(is_read=True)
    
    # Récupérer l'historique des messages
    messages = Message.objects.filter(
        Q(sender=current_user, receiver=other_user) |
        Q(sender=other_user, receiver=current_user)
    ).order_by('created_at')
    
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = current_user
            message.receiver = other_user
            message.save()
            
            # Créer une notification
            Notification.objects.create(
                recipient=other_user,
                notification_type='new_message',
                title=f"Nouveau message de {current_user.get_full_name()}",
                message=f"Vous avez reçu un nouveau message.",
                related_object_id=message.id,
                related_object_type='message'
            )
            
            return redirect('conversation', user_id=user_id)
    else:
        form = MessageForm()
    
    # Informations sur l'autre utilisateur
    other_user_info = {}
    try:
        if hasattr(other_user, 'freelancer'):
            other_user_info = {
                'type': 'freelancer',
                'profile': other_user.freelancer,
                'rating': other_user.freelancer.rating,
                'completed_projects': other_user.freelancer.completed_projects,
            }
        elif hasattr(other_user, 'client'):
            other_user_info = {
                'type': 'client',
                'profile': other_user.client,
                'total_projects': other_user.client.total_projects,
            }
    except:
        pass
    
    # Projets en commun (si applicable)
    common_projects = []
    if hasattr(current_user, 'client') and hasattr(other_user, 'freelancer'):
        common_projects = Project.objects.filter(
            client=current_user.client,
            selected_freelancer=other_user.freelancer
        ).order_by('-created_at')[:3]
    
    context = {
        'other_user': other_user,
        'other_user_info': other_user_info,
        'messages': messages,
        'form': form,
        'common_projects': common_projects,
    }
    
    return render(request, 'conversation.html', context)

def signup_client(request):
    """Inscription client avec validation avancée"""
    if request.method == 'POST':
        form = ClientSignUpForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            base_username = email.split('@')[0]
            username = base_username
            i = 1
            from django.contrib.auth.models import User
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{i}"
                i += 1
            user = form.save(commit=False)
            user.username = username
            user.email = email
            user.save()
            Client.objects.create(user=user)
            
            # Connexion automatique
            login(request, user)
            messages.success(request, "Compte client créé avec succès !")
            return redirect('dashboard')
    else:
        form = ClientSignUpForm()
    
    return render(request, 'inscription_client.html', {'form': form})

def signup_freelancer(request):
    """Inscription freelance avec validation avancée"""
    if request.method == 'POST':
        form = FreelancerSignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            
            # Créer le profil freelance
            freelancer = Freelancer.objects.create(
                user=user,
                hourly_rate=form.cleaned_data.get('hourly_rate', 0),
                description=form.cleaned_data.get('bio', ''),
                experience_years=form.cleaned_data.get('experience_years', 0),
                skills=[],
                languages=[]
            )
            
            # Connexion automatique
            login(request, user)
            messages.success(request, "Compte freelance créé avec succès !")
            return redirect('complete_profile')
    else:
        form = FreelancerSignUpForm()
    
    return render(request, 'inscription_freelancer.html', {'form': form})

def user_login(request):
    """Connexion avec fonctionnalités de sécurité et sélection de rôle"""
    # Récupérer le rôle depuis l'URL si présent
    role = request.GET.get('role')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                
                # Message de bienvenue personnalisé selon le rôle
                if role == 'client':
                    messages.success(request, f"Bienvenue Client, {user.get_full_name()} !")
                elif role == 'freelancer':
                    messages.success(request, f"Bienvenue Freelance, {user.get_full_name()} !")
                else:
                    messages.success(request, f"Bienvenue, {user.get_full_name()} !")
                
                # Redirection intelligente
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                else:
                    return redirect('dashboard')
            else:
                messages.error(request, "Email ou mot de passe incorrect.")
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form, 'role': role})

def user_logout(request):
    """Déconnexion"""
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect('home')

@login_required
def complete_profile(request):
    """Complétion du profil avec validation avancée"""
    try:
        freelancer = Freelancer.objects.get(user=request.user)
    except Freelancer.DoesNotExist:
        messages.error(request, "Profil non trouvé.")
        return redirect('home')
    
    if request.method == 'POST':
        form = FreelancerProfileForm(request.POST, request.FILES, instance=freelancer)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil complété avec succès !")
            return redirect('dashboard')
    else:
        form = FreelancerProfileForm(instance=freelancer)
    
    return render(request, 'complete_profile.html', {'form': form})

# API Views pour AJAX
@csrf_exempt
def api_notifications(request):
    """API pour récupérer les notifications non lues"""
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).order_by('-created_at')[:10]
        
        data = []
        for notif in notifications:
            data.append({
                'id': notif.id,
                'title': notif.title,
                'message': notif.message,
                'type': notif.notification_type,
                'created_at': notif.created_at.strftime('%d/%m/%Y %H:%M'),
                'is_important': notif.is_important,
            })
        
        return JsonResponse({'notifications': data})
    
    return JsonResponse({'notifications': []})

@csrf_exempt
def api_mark_notification_read(request):
    """API pour marquer une notification comme lue"""
    if request.user.is_authenticated and request.method == 'POST':
        notification_id = request.POST.get('notification_id')
        try:
            notification = Notification.objects.get(
                id=notification_id,
                recipient=request.user
            )
            notification.is_read = True
            notification.save()
            return JsonResponse({'success': True})
        except Notification.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Notification non trouvée'})
    
    return JsonResponse({'success': False, 'error': 'Requête invalide'})

@csrf_exempt
def api_search_suggestions(request):
    """API pour les suggestions de recherche"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    # Suggestions de projets
    project_suggestions = Project.objects.filter(
        title__icontains=query,
        status='open'
    ).values_list('title', flat=True)[:5]
    
    # Suggestions de compétences
    skill_suggestions = Skill.objects.filter(
        name__icontains=query
    ).values_list('name', flat=True)[:5]
    
    # Suggestions de freelances
    freelancer_suggestions = Freelancer.objects.filter(
        user__first_name__icontains=query
    ).values_list('user__first_name', flat=True)[:5]
    
    suggestions = list(project_suggestions) + list(skill_suggestions) + list(freelancer_suggestions)
    
    return JsonResponse({'suggestions': suggestions[:10]})


# Support Ticket Views
@login_required
def support_tickets(request):
    """
    View to display all support tickets for the current user
    """
    tickets = SupportTicket.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'support_tickets.html', {'tickets': tickets})


def admin_support_tickets(request):
    """
    Admin view to manage all support tickets
    """
    # Get filter parameters
    status = request.GET.get('status', '')
    priority = request.GET.get('priority', '')
    ticket_type = request.GET.get('type', '')
    
    # Start with all tickets
    tickets = SupportTicket.objects.all().order_by('-created_at')
    
    # Apply filters if provided
    if status:
        tickets = tickets.filter(status=status)
    if priority:
        tickets = tickets.filter(priority=priority)
    if ticket_type:
        tickets = tickets.filter(ticket_type=ticket_type)
    
    # Handle ticket assignment
    if request.method == 'POST':
        ticket_id = request.POST.get('ticket_id')
        action = request.POST.get('action')
        
        if ticket_id and action:
            ticket = get_object_or_404(SupportTicket, id=ticket_id)
            
            if action == 'assign':
                ticket.assigned_to = request.user
                ticket.status = 'in_progress'
                ticket.save()
                messages.success(request, f'Ticket #{ticket.id} assigned to you')
            
            elif action == 'close':
                ticket.status = 'closed'
                ticket.save()
                # Add a system response
                TicketResponse.objects.create(
                    ticket=ticket,
                    user=request.user,
                    message=f'Ticket closed by admin: {request.user.username}'
                )
                messages.success(request, f'Ticket #{ticket.id} closed')
            
            elif action == 'reopen':
                ticket.status = 'reopened'
                ticket.save()
                # Add a system response
                TicketResponse.objects.create(
                    ticket=ticket,
                    user=request.user,
                    message=f'Ticket reopened by admin: {request.user.username}'
                )
                messages.success(request, f'Ticket #{ticket.id} reopened')
    
    # Statistiques pour le dashboard
    open_tickets_count = SupportTicket.objects.filter(status='open').count()
    in_progress_count = SupportTicket.objects.filter(status='in_progress').count()
    resolved_count = SupportTicket.objects.filter(status='resolved').count()
    urgent_count = SupportTicket.objects.filter(priority='urgent').count()
    
    return render(request, 'admin_support_tickets.html', {
        'tickets': tickets,
        'status_filter': status,
        'priority_filter': priority,
        'type_filter': ticket_type,
        'open_tickets_count': open_tickets_count,
        'in_progress_count': in_progress_count,
        'resolved_count': resolved_count,
        'urgent_count': urgent_count
    })


def admin_validate_proposals(request):
    """
    Admin view to validate proposals before they are visible to clients
    """
    # Get filter parameters
    status = request.GET.get('status', 'pending')
    category_filter = request.GET.get('category', '')
    
    # Start with all proposals that need admin validation
    proposals = Proposal.objects.filter(admin_validation=status).order_by('-created_at')
    
    # Apply category filter if provided
    if category_filter:
        proposals = proposals.filter(project__category_id=category_filter)
    
    # Statistiques pour le dashboard
    pending_count = Proposal.objects.filter(admin_validation='pending').count()
    approved_count = Proposal.objects.filter(admin_validation='approved').count()
    rejected_count = Proposal.objects.filter(admin_validation='rejected').count()
    freelancers_count = Proposal.objects.values('freelancer').distinct().count()
    categories = Category.objects.all()
    
    return render(request, 'admin_validate_proposals.html', {
        'proposals': proposals,
        'status_filter': status,
        'category_filter': category_filter,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'freelancers_count': freelancers_count,
        'categories': categories
    })


def admin_validate_proposal(request, proposal_id):
    """
    Admin view to validate a specific proposal
    """
    proposal = get_object_or_404(Proposal, id=proposal_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        admin_comment = request.POST.get('admin_comment', '')
        
        if action == 'approve':
            proposal.admin_validation = 'approved'
            proposal.admin_comment = admin_comment
            proposal.status = 'pending'  # Change from pending_admin to pending
            proposal.save()
            
            # Create notification for the freelancer
            Notification.objects.create(
                recipient=proposal.freelancer.user,
                notification_type='proposal_accepted',
                title='Proposition approuvée',
                message=f'Votre proposition pour le projet "{proposal.project.title}" a été approuvée par l\'administrateur.',
                related_object_id=proposal.id,
                related_object_type='proposal'
            )
            
            # Update project proposals count
            project = proposal.project
            project.proposals_count += 1
            project.save()
            
            messages.success(request, f'Proposition #{proposal.id} approuvée')
            return redirect('admin_validate_proposals')
            
        elif action == 'reject':
            proposal.admin_validation = 'rejected'
            proposal.admin_comment = admin_comment
            proposal.status = 'rejected'
            proposal.save()
            
            # Create notification for the freelancer
            Notification.objects.create(
                recipient=proposal.freelancer.user,
                notification_type='proposal_rejected',
                title='Proposition rejetée',
                message=f'Votre proposition pour le projet "{proposal.project.title}" a été rejetée par l\'administrateur. Raison: {admin_comment}',
                related_object_id=proposal.id,
                related_object_type='proposal'
            )
            
            messages.success(request, f'Proposition #{proposal.id} rejetée')
            return redirect('admin_validate_proposals')
    
    return render(request, 'admin_validate_proposal.html', {
        'proposal': proposal
    })


@login_required
def create_support_ticket(request):
    """
    View to create a new support ticket
    """
    if request.method == 'POST':
        subject = request.POST.get('subject')
        description = request.POST.get('description')
        ticket_type = request.POST.get('ticket_type', 'other')
        priority = request.POST.get('priority')
        
        # Get related project if provided
        project_id = request.POST.get('project')
        project = None
        if project_id:
            try:
                project = Project.objects.get(id=project_id)
            except Project.DoesNotExist:
                pass
        
        # Create the ticket
        ticket = SupportTicket.objects.create(
            user=request.user,
            subject=subject,
            description=description,
            ticket_type=ticket_type,
            priority=priority,
            status='open',
            related_project=project
        )
        
        # Handle attachments if any
        if request.FILES.getlist('attachments'):
            for file in request.FILES.getlist('attachments'):
                ticket.attachments = file
                ticket.save()
        
        messages.success(request, 'Support ticket created successfully')
        return redirect('support_ticket_detail', ticket_id=ticket.id)
    
    # Get user's projects for the dropdown
    user_projects = []
    if hasattr(request.user, 'client'):
        user_projects = Project.objects.filter(client=request.user.client)
    elif hasattr(request.user, 'freelancer'):
        user_projects = Project.objects.filter(freelancer=request.user.freelancer)
    
    return render(request, 'create_support_ticket.html', {'user_projects': user_projects})


@login_required
def support_ticket_detail(request, ticket_id):
    """
    View to display a specific support ticket and its responses
    """
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    
    # Check if user is authorized to view this ticket
    if ticket.user != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this ticket')
        return redirect('support_tickets')
    
    # Handle new response submission
    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            response = TicketResponse.objects.create(
                ticket=ticket,
                user=request.user,
                message=message
            )
            
            # Update ticket status if it was closed
            if ticket.status == 'closed':
                ticket.status = 'reopened'
                ticket.save()
            
            messages.success(request, 'Response added successfully')
            return redirect('support_ticket_detail', ticket_id=ticket.id)
    
    # Get all responses for this ticket
    responses = TicketResponse.objects.filter(ticket=ticket).order_by('created_at')
    
    return render(request, 'support_ticket_detail.html', {
        'ticket': ticket,
        'responses': responses
    })


@login_required
def close_support_ticket(request, ticket_id):
    """
    View to close a support ticket
    """
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    
    # Check if user is authorized to close this ticket
    if ticket.user != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to close this ticket')
        return redirect('support_tickets')
    
    # Close the ticket
    ticket.status = 'closed'
    ticket.save()
    
    # Add a system response indicating the ticket was closed
    TicketResponse.objects.create(
        ticket=ticket,
        user=request.user,
        message=f'Ticket closed by {request.user.username}'
    )
    
    messages.success(request, 'Ticket closed successfully')
    return redirect('support_ticket_detail', ticket_id=ticket.id)

def validate_payment(request, payment_id):
    """Permettre aux clients de valider un paiement"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        payment = Payment.objects.get(id=payment_id, client=request.user.client)
        
        if request.method == 'POST':
            # Valider le paiement
            payment.status = 'completed'
            payment.save()
            
            # Créer une notification pour le freelance
            Notification.objects.create(
                recipient=payment.freelancer.user,
                notification_type='payment_received',
                title='Paiement reçu',
                message=f'Le paiement de {payment.amount}€ pour le projet "{payment.project.title}" a été validé.',
                related_object_id=payment.id,
                related_object_type='Payment'
            )
            
            messages.success(request, 'Paiement validé avec succès !')
            return redirect('dashboard')
        
        return render(request, 'validate_payment.html', {'payment': payment})
        
    except Payment.DoesNotExist:
        messages.error(request, 'Paiement non trouvé.')
        return redirect('dashboard')

def payment_history(request):
    """Historique des paiements"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    if hasattr(request.user, 'client'):
        payments = Payment.objects.filter(client=request.user.client).order_by('-created_at')
    elif hasattr(request.user, 'freelancer'):
        payments = Payment.objects.filter(freelancer=request.user.freelancer).order_by('-created_at')
    else:
        payments = []
    
    return render(request, 'payment_history.html', {'payments': payments})

def start_conversation(request, user_id):
    """Démarrer une nouvelle conversation"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    other_user = get_object_or_404(User, id=user_id)
    
    # Vérifier si une conversation existe déjà
    existing_conversation = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=request.user))
    ).first()
    
    if existing_conversation:
        # Rediriger vers la conversation existante
        return redirect('conversation', user_id=other_user.id)
    
    # Créer une nouvelle conversation avec un message de bienvenue
    welcome_message = Message.objects.create(
        sender=request.user,
        receiver=other_user,
        content=f"Bonjour ! Je souhaite discuter avec vous."
    )
    
    return redirect('conversation', user_id=other_user.id)
