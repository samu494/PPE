#!/usr/bin/env python
"""
Script de test pour vérifier que toutes les nouvelles fonctionnalités fonctionnent correctement
"""

import os
import sys
import django
from django.test import Client
from django.urls import reverse
from django.test.utils import override_settings

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freeafrique.settings')
django.setup()

@override_settings(ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'])
def test_home_page():
    """Test de la page d'accueil"""
    print("🔍 Test de la page d'accueil...")
    client = Client()
    response = client.get('/')
    
    if response.status_code == 200:
        print("✅ Page d'accueil accessible")
        
        # Vérifier les nouveaux éléments
        content = response.content.decode('utf-8')
        
        if 'Nouveau sur FreeAfrique ?' in content:
            print("✅ Section 'Nouveau sur FreeAfrique' présente")
        else:
            print("❌ Section 'Nouveau sur FreeAfrique' manquante")
            
        if 'Commencer maintenant' in content:
            print("✅ Lien 'Commencer maintenant' présent")
        else:
            print("❌ Lien 'Commencer maintenant' manquant")
            
        if 'Comment ça marche' in content:
            print("✅ Lien 'Comment ça marche' présent")
        else:
            print("❌ Lien 'Comment ça marche' manquant")
    else:
        print(f"❌ Erreur page d'accueil: {response.status_code}")

@override_settings(ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'])
def test_role_selection():
    """Test de la page de sélection de rôle"""
    print("\n🔍 Test de la page de sélection de rôle...")
    client = Client()
    response = client.get('/choisir-role/')
    
    if response.status_code == 200:
        print("✅ Page de sélection de rôle accessible")
        
        content = response.content.decode('utf-8')
        
        if 'Bienvenue sur FreeAfrique' in content:
            print("✅ Titre de bienvenue présent")
        else:
            print("❌ Titre de bienvenue manquant")
            
        if 'Je suis un Client' in content and 'Je suis un Freelance' in content:
            print("✅ Options Client et Freelance présentes")
        else:
            print("❌ Options Client et Freelance manquantes")
    else:
        print(f"❌ Erreur page sélection rôle: {response.status_code}")

@override_settings(ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'])
def test_how_it_works():
    """Test de la page 'Comment ça marche'"""
    print("\n🔍 Test de la page 'Comment ça marche'...")
    client = Client()
    response = client.get('/comment-ca-marche/')
    
    if response.status_code == 200:
        print("✅ Page 'Comment ça marche' accessible")
        
        content = response.content.decode('utf-8')
        
        if 'Pour les Clients' in content and 'Pour les Freelances' in content:
            print("✅ Sections Client et Freelance présentes")
        else:
            print("❌ Sections Client et Freelance manquantes")
    else:
        print(f"❌ Erreur page 'Comment ça marche': {response.status_code}")

@override_settings(ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'])
def test_first_time_guide():
    """Test de la page guide première fois"""
    print("\n🔍 Test de la page guide première fois...")
    client = Client()
    response = client.get('/guide-premiere-fois/')
    
    if response.status_code == 200:
        print("✅ Page guide première fois accessible")
        
        content = response.content.decode('utf-8')
        
        if 'Bienvenue sur FreeAfrique !' in content:
            print("✅ Titre de bienvenue présent")
        else:
            print("❌ Titre de bienvenue manquant")
    else:
        print(f"❌ Erreur page guide première fois: {response.status_code}")

@override_settings(ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'])
def test_admin_pages():
    """Test des pages d'administration"""
    print("\n🔍 Test des pages d'administration...")
    client = Client()
    
    # Test du tableau de bord admin
    response = client.get('/admin/dashboard/')
    if response.status_code == 302:  # Redirection vers login
        print("✅ Page tableau de bord admin (redirection login)")
    elif response.status_code == 200:
        print("✅ Page tableau de bord admin accessible")
    else:
        print(f"❌ Erreur tableau de bord admin: {response.status_code}")
    
    # Test des statistiques admin
    response = client.get('/admin/statistics/')
    if response.status_code == 302:  # Redirection vers login
        print("✅ Page statistiques admin (redirection login)")
    elif response.status_code == 200:
        print("✅ Page statistiques admin accessible")
    else:
        print(f"❌ Erreur statistiques admin: {response.status_code}")

@override_settings(ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'])
def test_support_pages():
    """Test des pages de support"""
    print("\n🔍 Test des pages de support...")
    client = Client()
    
    # Test de la liste des tickets
    response = client.get('/support/')
    if response.status_code == 302:  # Redirection vers login
        print("✅ Page tickets support (redirection login)")
    elif response.status_code == 200:
        print("✅ Page tickets support accessible")
    else:
        print(f"❌ Erreur tickets support: {response.status_code}")
    
    # Test de création de ticket
    response = client.get('/support/create/')
    if response.status_code == 302:  # Redirection vers login
        print("✅ Page création ticket (redirection login)")
    elif response.status_code == 200:
        print("✅ Page création ticket accessible")
    else:
        print(f"❌ Erreur création ticket: {response.status_code}")

@override_settings(ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'])
def test_payment_pages():
    """Test des pages de paiement"""
    print("\n🔍 Test des pages de paiement...")
    client = Client()
    
    # Test de la page des méthodes de paiement
    response = client.get('/payment/methods/')
    if response.status_code == 302:  # Redirection vers login
        print("✅ Page méthodes de paiement (redirection login)")
    elif response.status_code == 200:
        print("✅ Page méthodes de paiement accessible")
    else:
        print(f"❌ Erreur méthodes de paiement: {response.status_code}")

@override_settings(ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'])
def test_back_buttons():
    """Test des boutons de retour"""
    print("\n🔍 Test des boutons de retour...")
    client = Client()
    
    # Test de la page de création de projet
    response = client.get('/projects/create/')
    if response.status_code == 302:  # Redirection vers login
        print("✅ Page création projet (redirection login)")
    elif response.status_code == 200:
        content = response.content.decode('utf-8')
        if 'Retour aux projets' in content:
            print("✅ Bouton retour présent sur création projet")
        else:
            print("❌ Bouton retour manquant sur création projet")
    else:
        print(f"❌ Erreur création projet: {response.status_code}")

def main():
    """Fonction principale de test"""
    print("🚀 Démarrage des tests de fonctionnalités...")
    print("=" * 50)
    
    test_home_page()
    test_role_selection()
    test_how_it_works()
    test_first_time_guide()
    test_admin_pages()
    test_support_pages()
    test_payment_pages()
    test_back_buttons()
    
    print("\n" + "=" * 50)
    print("✅ Tests terminés!")

if __name__ == '__main__':
    main()
