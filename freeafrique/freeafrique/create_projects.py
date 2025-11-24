from django.contrib.auth.models import User
from main.models import Category, Client, Project
import random
from datetime import date, timedelta

# Données pour les projets
project_data = [
    {
        'title': 'Site web e-commerce pour boutique de mode',
        'description': 'Création d\'un site web e-commerce moderne pour une boutique de mode africaine. Fonctionnalités : catalogue produits, panier, paiement en ligne, gestion des commandes.',
        'category': 'Développement Web',
        'budget_min': 1500,
        'budget_max': 3000,
        'required_skills': ['Développement Web', 'E-commerce'],
        'deadline_days': 30
    },
    {
        'title': 'Identité visuelle pour startup tech',
        'description': 'Création complète de l\'identité visuelle : logo, charte graphique, cartes de visite, templates pour réseaux sociaux.',
        'category': 'Design',
        'budget_min': 800,
        'budget_max': 1500,
        'required_skills': ['Design', 'Branding'],
        'deadline_days': 15
    },
    {
        'title': 'Campagne marketing pour lancement produit',
        'description': 'Stratégie marketing complète pour le lancement d\'un nouveau produit : publicités Google/Facebook, contenu web, influenceurs.',
        'category': 'Marketing Digital',
        'budget_min': 2000,
        'budget_max': 4000,
        'required_skills': ['Marketing Digital', 'Publicité'],
        'deadline_days': 45
    },
    {
        'title': 'Application mobile de livraison',
        'description': 'Développement d\'une application mobile pour service de livraison : géolocalisation, suivi en temps réel, notifications push.',
        'category': 'Développement Mobile',
        'budget_min': 3000,
        'budget_max': 6000,
        'required_skills': ['Développement Mobile', 'Géolocalisation'],
        'deadline_days': 60
    },
    {
        'title': 'Traduction site web multilingue',
        'description': 'Traduction complète d\'un site web de français vers anglais et arabe. Contenu technique et commercial.',
        'category': 'Traduction',
        'budget_min': 500,
        'budget_max': 1000,
        'required_skills': ['Traduction', 'Français', 'Anglais'],
        'deadline_days': 20
    },
    {
        'title': 'Vidéo promotionnelle entreprise',
        'description': 'Création d\'une vidéo promotionnelle 2-3 minutes pour présenter l\'entreprise : script, tournage, montage, effets visuels.',
        'category': 'Vidéo',
        'budget_min': 1200,
        'budget_max': 2500,
        'required_skills': ['Vidéo', 'Montage'],
        'deadline_days': 25
    },
    {
        'title': 'Podcast série documentaire',
        'description': 'Production d\'une série de 10 épisodes de podcast sur l\'entrepreneuriat en Afrique : recherche, interviews, montage audio.',
        'category': 'Audio',
        'budget_min': 800,
        'budget_max': 1800,
        'required_skills': ['Audio', 'Podcast'],
        'deadline_days': 40
    },
    {
        'title': 'Blog contenu marketing',
        'description': 'Rédaction de 20 articles de blog optimisés SEO pour une entreprise de services financiers. Thèmes : finance, investissement, économie.',
        'category': 'Rédaction',
        'budget_min': 600,
        'budget_max': 1200,
        'required_skills': ['Rédaction', 'SEO'],
        'deadline_days': 30
    },
    {
        'title': 'Illustrations pour livre jeunesse',
        'description': 'Création de 15 illustrations colorées pour un livre jeunesse sur les contes africains. Style moderne et adapté aux enfants.',
        'category': 'Graphisme',
        'budget_min': 400,
        'budget_max': 800,
        'required_skills': ['Graphisme', 'Illustration'],
        'deadline_days': 20
    },
    {
        'title': 'Application web de gestion RH',
        'description': 'Développement d\'une application web pour la gestion des ressources humaines : recrutement, suivi des employés, congés, paie.',
        'category': 'Développement Web',
        'budget_min': 2500,
        'budget_max': 5000,
        'required_skills': ['Développement Web', 'Gestion'],
        'deadline_days': 90
    }
]

print("Création des clients et projets...")

# Créer les clients et projets
for i, data in enumerate(project_data):
    # Créer l'utilisateur client
    username = f"client{i+1}"
    try:
        user = User.objects.get(username=username)
        print(f"Client existant trouvé : {username}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=username,
            email=f"client{i+1}@email.com",
            password='password123',
            first_name=f"Client{i+1}",
            last_name="Test"
        )
        print(f"Client créé : {username}")
    
    # Créer ou récupérer le profil client
    client, created = Client.objects.get_or_create(
        user=user,
        defaults={
            'company_name': f"Entreprise {i+1}",
            'company_description': f"Description de l'entreprise {i+1}",
            'location': random.choice(['Dakar', 'Abidjan', 'Lagos', 'Nairobi', 'Accra']),
            'is_verified': random.choice([True, False])
        }
    )
    
    # Trouver la catégorie ou utiliser la première disponible
    try:
        category = Category.objects.get(name=data['category'])
    except Category.DoesNotExist:
        category = Category.objects.first()
    
    # Créer le projet
    project = Project.objects.create(
        title=data['title'],
        description=data['description'],
        category=category,
        client=client,
        budget_min=data['budget_min'],
        budget_max=data['budget_max'],
        budget_type=random.choice(['fixed', 'hourly', 'negotiable']),
        deadline=date.today() + timedelta(days=data['deadline_days']),
        required_skills=data['required_skills'],
        status=random.choice(['open', 'open', 'open', 'in_progress']),
        is_featured=random.choice([True, False]),
        is_urgent=random.choice([True, False]),
        views_count=random.randint(10, 200),
        proposals_count=random.randint(0, 8)
    )
    print(f"Projet créé : {data['title']}")

print(f"\n✅ Création terminée !")
print(f"📊 Statistiques :")
print(f"   - {len(project_data)} projets créés")


