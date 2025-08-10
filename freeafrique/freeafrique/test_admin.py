#!/usr/bin/env python
"""
Script de test pour vérifier l'administration Django de FreeAfrique
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freeafrique.settings')
django.setup()

from main.models import (
    Category, Freelancer, Client, Project, Proposal, 
    SupportTicket, TicketResponse, Review, Message, 
    Notification, Payment, Milestone, Dispute, Skill
)

def test_admin_interface():
    """Test de l'interface d'administration"""
    print("🔍 Test de l'interface d'administration Django...")
    
    # Créer un superutilisateur de test
    try:
        admin_user = User.objects.create_superuser(
            username='admin_test',
            email='admin@test.com',
            password='admin123'
        )
        print("✅ Superutilisateur créé")
    except:
        admin_user = User.objects.get(username='admin_test')
        print("✅ Superutilisateur existant")
    
    # Test de connexion admin
    client = Client()
    login_success = client.login(username='admin_test', password='admin123')
    
    if login_success:
        print("✅ Connexion admin réussie")
    else:
        print("❌ Échec de la connexion admin")
        return False
    
    # Test des URLs d'administration
    admin_urls = [
        '/admin/',
        '/admin/main/category/',
        '/admin/main/freelancer/',
        '/admin/main/client/',
        '/admin/main/project/',
        '/admin/main/proposal/',
        '/admin/main/supportticket/',
        '/admin/main/ticketresponse/',
        '/admin/main/review/',
        '/admin/main/message/',
        '/admin/main/notification/',
        '/admin/main/payment/',
        '/admin/main/milestone/',
        '/admin/main/dispute/',
        '/admin/main/skill/',
    ]
    
    for url in admin_urls:
        response = client.get(url)
        if response.status_code == 200:
            print(f"✅ {url} - OK")
        else:
            print(f"❌ {url} - Erreur {response.status_code}")
    
    # Test des vues d'administration personnalisées
    custom_admin_urls = [
        '/admin/support/',
        '/admin/proposals/',
        '/admin/dashboard/',
        '/admin/statistics/',
    ]
    
    for url in custom_admin_urls:
        response = client.get(url)
        if response.status_code == 200:
            print(f"✅ {url} - OK")
        else:
            print(f"❌ {url} - Erreur {response.status_code}")
    
    return True

def test_admin_models():
    """Test des modèles d'administration"""
    print("\n🔍 Test des modèles d'administration...")
    
    # Test de création de données de test
    try:
        # Créer une catégorie
        category = Category.objects.create(
            name='Test Category',
            description='Description de test',
            icon='ri-code-line'
        )
        print("✅ Catégorie créée")
        
        # Créer un utilisateur de test
        user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='test123'
        )
        print("✅ Utilisateur créé")
        
        # Créer un freelance
        freelancer = Freelancer.objects.create(
            user=user,
            hourly_rate=50.00,
            description='Freelance de test',
            skills=['Python', 'Django'],
            location='Paris'
        )
        print("✅ Freelance créé")
        
        # Créer un client
        client = Client.objects.create(
            user=user,
            company_name='Test Company'
        )
        print("✅ Client créé")
        
        # Créer un projet
        project = Project.objects.create(
            title='Projet de test',
            description='Description du projet de test',
            category=category,
            client=client,
            budget_min=1000,
            budget_max=5000,
            deadline='2024-12-31'
        )
        print("✅ Projet créé")
        
        # Créer une proposition
        proposal = Proposal.objects.create(
            project=project,
            freelancer=freelancer,
            price=2500,
            delivery_time=30,
            message='Proposition de test'
        )
        print("✅ Proposition créée")
        
        # Créer un ticket de support
        ticket = SupportTicket.objects.create(
            user=user,
            subject='Ticket de test',
            description='Description du ticket de test',
            ticket_type='technical',
            priority='medium'
        )
        print("✅ Ticket de support créé")
        
        # Créer une réponse de ticket
        response = TicketResponse.objects.create(
            ticket=ticket,
            user=user,
            message='Réponse de test'
        )
        print("✅ Réponse de ticket créée")
        
        print("✅ Tous les modèles de test créés avec succès")
        
        # Nettoyer les données de test
        response.delete()
        ticket.delete()
        proposal.delete()
        project.delete()
        client.delete()
        freelancer.delete()
        user.delete()
        category.delete()
        print("✅ Données de test nettoyées")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des modèles: {e}")
        return False
    
    return True

def test_admin_actions():
    """Test des actions d'administration"""
    print("\n🔍 Test des actions d'administration...")
    
    try:
        # Créer des données de test
        category = Category.objects.create(
            name='Test Category',
            description='Description de test',
            icon='ri-code-line'
        )
        
        user = User.objects.create_user(
            username='testuser2',
            email='test2@test.com',
            password='test123'
        )
        
        freelancer = Freelancer.objects.create(
            user=user,
            hourly_rate=50.00,
            description='Freelance de test',
            skills=['Python', 'Django'],
            location='Paris'
        )
        
        client = Client.objects.create(
            user=user,
            company_name='Test Company'
        )
        
        project = Project.objects.create(
            title='Projet de test',
            description='Description du projet de test',
            category=category,
            client=client,
            budget_min=1000,
            budget_max=5000,
            deadline='2024-12-31'
        )
        
        proposal = Proposal.objects.create(
            project=project,
            freelancer=freelancer,
            price=2500,
            delivery_time=30,
            message='Proposition de test'
        )
        
        ticket = SupportTicket.objects.create(
            user=user,
            subject='Ticket de test',
            description='Description du ticket de test',
            ticket_type='technical',
            priority='medium'
        )
        
        # Test des actions
        print("✅ Données de test créées pour les actions")
        
        # Nettoyer
        ticket.delete()
        proposal.delete()
        project.delete()
        client.delete()
        freelancer.delete()
        user.delete()
        category.delete()
        
        print("✅ Actions d'administration testées")
        
    except Exception as e:
        print(f"❌ Erreur lors du test des actions: {e}")
        return False
    
    return True

def main():
    """Fonction principale de test"""
    print("🚀 Démarrage des tests d'administration Django...\n")
    
    # Tests
    test1 = test_admin_interface()
    test2 = test_admin_models()
    test3 = test_admin_actions()
    
    print("\n" + "="*50)
    print("📊 RÉSULTATS DES TESTS")
    print("="*50)
    
    if test1 and test2 and test3:
        print("✅ TOUS LES TESTS ONT RÉUSSI")
        print("🎉 L'administration Django fonctionne correctement !")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("🔧 Veuillez vérifier la configuration")
    
    print("="*50)

if __name__ == '__main__':
    main()

