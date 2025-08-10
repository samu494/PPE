#!/usr/bin/env python
import os
import sys
import django
from django.contrib.auth.models import User
from main.models import Category, Freelancer, Client, Project, Skill, Notification
from datetime import date, timedelta
import random

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freeafrique.settings')
django.setup()

def create_categories():
    """Créer les catégories de projets"""
    categories_data = [
        {
            'name': 'Développement Web',
            'description': 'Sites web, applications web, e-commerce, CMS',
            'icon': 'ri-code-s-slash-line',
            'color': '#3b82f6',
            'is_featured': True,
        },
        {
            'name': 'Design Graphique',
            'description': 'Logos, identité visuelle, maquettes, illustrations',
            'icon': 'ri-palette-line',
            'color': '#10b981',
            'is_featured': True,
        },
        {
            'name': 'Rédaction & Traduction',
            'description': 'Articles, contenus web, traductions, copywriting',
            'icon': 'ri-file-text-line',
            'color': '#f59e0b',
            'is_featured': True,
        },
        {
            'name': 'Marketing Digital',
            'description': 'SEO, publicité, réseaux sociaux, email marketing',
            'icon': 'ri-line-chart-line',
            'color': '#ef4444',
            'is_featured': True,
        },
        {
            'name': 'Vidéo & Animation',
            'description': 'Montage vidéo, animations, motion design',
            'icon': 'ri-video-line',
            'color': '#8b5cf6',
            'is_featured': False,
        },
        {
            'name': 'Audio & Podcast',
            'description': 'Montage audio, podcasts, voix off',
            'icon': 'ri-volume-up-line',
            'color': '#06b6d4',
            'is_featured': False,
        },
        {
            'name': 'Mobile Development',
            'description': 'Applications iOS, Android, React Native',
            'icon': 'ri-smartphone-line',
            'color': '#84cc16',
            'is_featured': True,
        },
        {
            'name': 'Data Science',
            'description': 'Analyse de données, machine learning, IA',
            'icon': 'ri-database-2-line',
            'color': '#f97316',
            'is_featured': False,
        },
    ]
    
    for data in categories_data:
        category, created = Category.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        if created:
            print(f"Catégorie créée: {category.name}")

def create_skills():
    """Créer les compétences populaires"""
    skills_data = [
        # Développement Web
        {'name': 'HTML/CSS', 'category': 'Développement Web', 'icon': 'ri-code-s-slash-line', 'is_popular': True},
        {'name': 'JavaScript', 'category': 'Développement Web', 'icon': 'ri-code-s-slash-line', 'is_popular': True},
        {'name': 'React', 'category': 'Développement Web', 'icon': 'ri-code-s-slash-line', 'is_popular': True},
        {'name': 'Vue.js', 'category': 'Développement Web', 'icon': 'ri-code-s-slash-line', 'is_popular': True},
        {'name': 'Node.js', 'category': 'Développement Web', 'icon': 'ri-code-s-slash-line', 'is_popular': True},
        {'name': 'Python', 'category': 'Développement Web', 'icon': 'ri-code-s-slash-line', 'is_popular': True},
        {'name': 'Django', 'category': 'Développement Web', 'icon': 'ri-code-s-slash-line', 'is_popular': True},
        {'name': 'Laravel', 'category': 'Développement Web', 'icon': 'ri-code-s-slash-line', 'is_popular': True},
        {'name': 'WordPress', 'category': 'Développement Web', 'icon': 'ri-code-s-slash-line', 'is_popular': True},
        
        # Design Graphique
        {'name': 'Photoshop', 'category': 'Design Graphique', 'icon': 'ri-palette-line', 'is_popular': True},
        {'name': 'Illustrator', 'category': 'Design Graphique', 'icon': 'ri-palette-line', 'is_popular': True},
        {'name': 'Figma', 'category': 'Design Graphique', 'icon': 'ri-palette-line', 'is_popular': True},
        {'name': 'InDesign', 'category': 'Design Graphique', 'icon': 'ri-palette-line', 'is_popular': False},
        {'name': 'Sketch', 'category': 'Design Graphique', 'icon': 'ri-palette-line', 'is_popular': False},
        
        # Rédaction
        {'name': 'Copywriting', 'category': 'Rédaction & Traduction', 'icon': 'ri-file-text-line', 'is_popular': True},
        {'name': 'SEO', 'category': 'Rédaction & Traduction', 'icon': 'ri-file-text-line', 'is_popular': True},
        {'name': 'Traduction', 'category': 'Rédaction & Traduction', 'icon': 'ri-file-text-line', 'is_popular': True},
        {'name': 'Blog', 'category': 'Rédaction & Traduction', 'icon': 'ri-file-text-line', 'is_popular': True},
        
        # Marketing
        {'name': 'Google Ads', 'category': 'Marketing Digital', 'icon': 'ri-line-chart-line', 'is_popular': True},
        {'name': 'Facebook Ads', 'category': 'Marketing Digital', 'icon': 'ri-line-chart-line', 'is_popular': True},
        {'name': 'Email Marketing', 'category': 'Marketing Digital', 'icon': 'ri-line-chart-line', 'is_popular': True},
        {'name': 'LinkedIn', 'category': 'Marketing Digital', 'icon': 'ri-line-chart-line', 'is_popular': True},
        
        # Mobile
        {'name': 'React Native', 'category': 'Mobile Development', 'icon': 'ri-smartphone-line', 'is_popular': True},
        {'name': 'Flutter', 'category': 'Mobile Development', 'icon': 'ri-smartphone-line', 'is_popular': True},
        {'name': 'iOS', 'category': 'Mobile Development', 'icon': 'ri-smartphone-line', 'is_popular': True},
        {'name': 'Android', 'category': 'Mobile Development', 'icon': 'ri-smartphone-line', 'is_popular': True},
    ]
    
    for data in skills_data:
        category = Category.objects.get(name=data['category'])
        skill, created = Skill.objects.get_or_create(
            name=data['name'],
            defaults={
                'category': category,
                'icon': data['icon'],
                'is_popular': data['is_popular']
            }
        )
        if created:
            print(f"Compétence créée: {skill.name}")

def create_test_users():
    """Créer des utilisateurs de test"""
    
    # Créer un superuser admin
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@freeafrique.com',
            'first_name': 'Admin',
            'last_name': 'FreeAfrique',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("Superuser admin créé")
    
    # Créer des clients de test
    clients_data = [
        {
            'username': 'client1',
            'email': 'client1@example.com',
            'first_name': 'Marie',
            'last_name': 'Dubois',
            'company_name': 'TechStart Africa',
            'company_description': 'Startup innovante dans le domaine de la fintech',
        },
        {
            'username': 'client2',
            'email': 'client2@example.com',
            'first_name': 'Ahmed',
            'last_name': 'Diallo',
            'company_name': 'Digital Solutions',
            'company_description': 'Agence de marketing digital',
        },
        {
            'username': 'client3',
            'email': 'client3@example.com',
            'first_name': 'Fatou',
            'last_name': 'Ndiaye',
            'company_name': 'E-commerce Plus',
            'company_description': 'Plateforme e-commerce spécialisée',
        },
    ]
    
    for data in clients_data:
        user, created = User.objects.get_or_create(
            username=data['username'],
            defaults={
                'email': data['email'],
                'first_name': data['first_name'],
                'last_name': data['last_name'],
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            
            client, client_created = Client.objects.get_or_create(
                user=user,
                defaults={
                    'company_name': data['company_name'],
                    'company_description': data['company_description'],
                    'location': random.choice(['Dakar', 'Abidjan', 'Lagos', 'Nairobi', 'Casablanca']),
                    'is_verified': True,
                }
            )
            if client_created:
                print(f"Client créé: {user.get_full_name()}")
    
    # Créer des freelances de test
    freelancers_data = [
        {
            'username': 'freelancer1',
            'email': 'freelancer1@example.com',
            'first_name': 'Kofi',
            'last_name': 'Mensah',
            'hourly_rate': 45.00,
            'description': 'Développeur web full-stack avec 5 ans d\'expérience. Spécialisé en React, Node.js et Python.',
            'skills': ['React', 'Node.js', 'Python', 'Django', 'MongoDB'],
            'experience_years': 5,
            'location': 'Accra',
            'is_verified': True,
            'is_featured': True,
        },
        {
            'username': 'freelancer2',
            'email': 'freelancer2@example.com',
            'first_name': 'Aisha',
            'last_name': 'Omar',
            'hourly_rate': 35.00,
            'description': 'Designer graphique créative avec un œil pour les détails. Spécialisée en branding et UI/UX.',
            'skills': ['Photoshop', 'Illustrator', 'Figma', 'UI/UX Design'],
            'experience_years': 3,
            'location': 'Nairobi',
            'is_verified': True,
            'is_featured': True,
        },
        {
            'username': 'freelancer3',
            'email': 'freelancer3@example.com',
            'first_name': 'Moussa',
            'last_name': 'Traoré',
            'hourly_rate': 25.00,
            'description': 'Rédacteur web et copywriter passionné. Je crée du contenu engageant qui convertit.',
            'skills': ['Copywriting', 'SEO', 'Blog', 'Email Marketing'],
            'experience_years': 4,
            'location': 'Bamako',
            'is_verified': True,
            'is_featured': False,
        },
        {
            'username': 'freelancer4',
            'email': 'freelancer4@example.com',
            'first_name': 'Zara',
            'last_name': 'Bello',
            'hourly_rate': 40.00,
            'description': 'Spécialiste en marketing digital avec expertise en publicité en ligne et réseaux sociaux.',
            'skills': ['Google Ads', 'Facebook Ads', 'LinkedIn', 'Email Marketing'],
            'experience_years': 6,
            'location': 'Lagos',
            'is_verified': True,
            'is_featured': True,
        },
        {
            'username': 'freelancer5',
            'email': 'freelancer5@example.com',
            'first_name': 'Youssef',
            'last_name': 'Benali',
            'hourly_rate': 50.00,
            'description': 'Développeur mobile expérimenté spécialisé en React Native et Flutter.',
            'skills': ['React Native', 'Flutter', 'iOS', 'Android', 'Firebase'],
            'experience_years': 7,
            'location': 'Casablanca',
            'is_verified': True,
            'is_featured': True,
        },
        {
            'username': 'freelancer6',
            'email': 'freelancer6@example.com',
            'first_name': 'Grace',
            'last_name': 'Akinyi',
            'hourly_rate': 30.00,
            'description': 'Vidéaste et monteuse créative. Je donne vie à vos histoires à travers la vidéo.',
            'skills': ['Premiere Pro', 'After Effects', 'Motion Design', 'Cinema 4D'],
            'experience_years': 4,
            'location': 'Kampala',
            'is_verified': True,
            'is_featured': False,
        },
    ]
    
    for data in freelancers_data:
        user, created = User.objects.get_or_create(
            username=data['username'],
            defaults={
                'email': data['email'],
                'first_name': data['first_name'],
                'last_name': data['last_name'],
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            
            freelancer, freelancer_created = Freelancer.objects.get_or_create(
                user=user,
                defaults={
                    'hourly_rate': data['hourly_rate'],
                    'description': data['description'],
                    'skills': data['skills'],
                    'experience_years': data['experience_years'],
                    'location': data['location'],
                    'is_verified': data['is_verified'],
                    'is_featured': data['is_featured'],
                    'rating': round(random.uniform(4.0, 5.0), 1),
                    'total_reviews': random.randint(10, 50),
                    'completed_projects': random.randint(5, 25),
                    'total_earnings': random.randint(5000, 25000),
                }
            )
            if freelancer_created:
                print(f"Freelance créé: {user.get_full_name()}")

def create_test_projects():
    """Créer des projets de test"""
    clients = Client.objects.all()
    categories = Category.objects.all()
    
    projects_data = [
        {
            'title': 'Site E-commerce Moderne',
            'description': 'Création d\'un site e-commerce complet avec système de paiement, gestion des stocks et interface admin. Le site doit être responsive et optimisé SEO.',
            'category': 'Développement Web',
            'budget_min': 3000,
            'budget_max': 8000,
            'budget_type': 'fixed',
            'required_skills': ['React', 'Node.js', 'MongoDB', 'Stripe'],
            'additional_info': 'Projet urgent pour lancement en 2 mois',
            'is_featured': True,
            'is_urgent': True,
        },
        {
            'title': 'Identité Visuelle Startup',
            'description': 'Création complète de l\'identité visuelle : logo, charte graphique, cartes de visite, templates email et réseaux sociaux.',
            'category': 'Design Graphique',
            'budget_min': 800,
            'budget_max': 2000,
            'budget_type': 'fixed',
            'required_skills': ['Photoshop', 'Illustrator', 'Branding'],
            'additional_info': 'Style moderne et professionnel',
            'is_featured': True,
            'is_urgent': False,
        },
        {
            'title': 'Articles Blog Tech',
            'description': 'Rédaction de 10 articles de blog sur les dernières tendances technologiques. Articles de 1500 mots minimum avec recherche SEO.',
            'category': 'Rédaction & Traduction',
            'budget_min': 500,
            'budget_max': 1200,
            'budget_type': 'fixed',
            'required_skills': ['Copywriting', 'SEO', 'Blog'],
            'additional_info': 'Ton professionnel mais accessible',
            'is_featured': False,
            'is_urgent': False,
        },
        {
            'title': 'Campagne Marketing Digital',
            'description': 'Gestion complète d\'une campagne marketing sur Google Ads et Facebook Ads pour une startup fintech.',
            'category': 'Marketing Digital',
            'budget_min': 2000,
            'budget_max': 5000,
            'budget_type': 'fixed',
            'required_skills': ['Google Ads', 'Facebook Ads', 'Analytics'],
            'additional_info': 'Budget publicitaire de 10k€ à gérer',
            'is_featured': True,
            'is_urgent': True,
        },
        {
            'title': 'App Mobile React Native',
            'description': 'Développement d\'une application mobile de livraison de repas avec géolocalisation et paiement intégré.',
            'category': 'Mobile Development',
            'budget_min': 5000,
            'budget_max': 15000,
            'budget_type': 'fixed',
            'required_skills': ['React Native', 'Firebase', 'Maps API'],
            'additional_info': 'Projet sur 3 mois avec phases de développement',
            'is_featured': True,
            'is_urgent': False,
        },
        {
            'title': 'Vidéo Corporate',
            'description': 'Création d\'une vidéo corporate de 2-3 minutes pour présenter l\'entreprise. Montage professionnel avec animations.',
            'category': 'Vidéo & Animation',
            'budget_min': 1500,
            'budget_max': 3000,
            'budget_type': 'fixed',
            'required_skills': ['Premiere Pro', 'After Effects', 'Motion Design'],
            'additional_info': 'Matériel fourni par le client',
            'is_featured': False,
            'is_urgent': False,
        },
        {
            'title': 'Site WordPress E-commerce',
            'description': 'Création d\'un site WordPress avec WooCommerce pour vente de produits artisanaux. Design personnalisé et optimisation SEO.',
            'category': 'Développement Web',
            'budget_min': 1200,
            'budget_max': 3000,
            'budget_type': 'fixed',
            'required_skills': ['WordPress', 'WooCommerce', 'PHP', 'CSS'],
            'additional_info': 'Site multilingue français/anglais',
            'is_featured': False,
            'is_urgent': False,
        },
        {
            'title': 'Traduction Site Web',
            'description': 'Traduction complète d\'un site web de l\'anglais vers le français (50 pages). Adaptation culturelle incluse.',
            'category': 'Rédaction & Traduction',
            'budget_min': 800,
            'budget_max': 2000,
            'budget_type': 'fixed',
            'required_skills': ['Traduction', 'SEO', 'Localisation'],
            'additional_info': 'Deadline : 2 semaines',
            'is_featured': False,
            'is_urgent': True,
        },
    ]
    
    for data in projects_data:
        client = random.choice(clients)
        category = Category.objects.get(name=data['category'])
        
        project, created = Project.objects.get_or_create(
            title=data['title'],
            defaults={
                'description': data['description'],
                'category': category,
                'client': client,
                'budget_min': data['budget_min'],
                'budget_max': data['budget_max'],
                'budget_type': data['budget_type'],
                'deadline': date.today() + timedelta(days=random.randint(15, 60)),
                'required_skills': data['required_skills'],
                'additional_info': data['additional_info'],
                'status': 'open',
                'is_featured': data['is_featured'],
                'is_urgent': data['is_urgent'],
                'views_count': random.randint(10, 100),
                'proposals_count': random.randint(0, 8),
            }
        )
        if created:
            print(f"Projet créé: {project.title}")

def create_notifications():
    """Créer des notifications de test"""
    users = User.objects.all()
    
    notifications_data = [
        {
            'title': 'Bienvenue sur FreeAfrique !',
            'message': 'Votre compte a été créé avec succès. Commencez par compléter votre profil.',
            'notification_type': 'system_alert',
            'is_important': True,
        },
        {
            'title': 'Nouveau projet disponible',
            'message': 'Un nouveau projet correspond à vos compétences. Consultez-le maintenant !',
            'notification_type': 'project_proposal',
            'is_important': False,
        },
        {
            'title': 'Proposition acceptée',
            'message': 'Félicitations ! Votre proposition a été acceptée. Contactez votre client.',
            'notification_type': 'proposal_accepted',
            'is_important': True,
        },
    ]
    
    for user in users[:3]:  # Notifications pour les 3 premiers utilisateurs
        for data in notifications_data:
            Notification.objects.get_or_create(
                recipient=user,
                title=data['title'],
                defaults={
                    'message': data['message'],
                    'notification_type': data['notification_type'],
                    'is_important': data['is_important'],
                }
            )
    
    print("Notifications de test créées")

def main():
    """Fonction principale pour charger toutes les données"""
    print("Début du chargement des données...")
    
    create_categories()
    create_skills()
    create_test_users()
    create_test_projects()
    create_notifications()
    
    print("\n✅ Chargement des données terminé !")
    print("\n📋 Comptes de test créés :")
    print("👤 Admin: admin / admin123")
    print("👥 Clients: client1, client2, client3 / password123")
    print("💼 Freelances: freelancer1, freelancer2, freelancer3, freelancer4, freelancer5, freelancer6 / password123")

if __name__ == '__main__':
    main() 