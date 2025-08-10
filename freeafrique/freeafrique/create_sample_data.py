from django.contrib.auth.models import User
from main.models import Category, Freelancer, Client, Project
import random

# Récupérer les catégories
categories = list(Category.objects.all())

# Données pour les freelances
freelancer_data = [
    {
        'first_name': 'Amadou',
        'last_name': 'Diallo',
        'email': 'amadou.diallo@email.com',
        'hourly_rate': 25.00,
        'description': 'Développeur web fullstack avec 5 ans d\'expérience en React, Node.js et Python. Spécialisé dans les applications web modernes.',
        'skills': ['Développement Web', 'React', 'Node.js'],
        'experience_years': 5,
        'location': 'Dakar, Sénégal',
        'rating': 4.8,
        'completed_projects': 15
    },
    {
        'first_name': 'Fatou',
        'last_name': 'Ndiaye',
        'email': 'fatou.ndiaye@email.com',
        'hourly_rate': 30.00,
        'description': 'Designer UI/UX créative avec une passion pour l\'expérience utilisateur. Expert en Figma et Adobe Creative Suite.',
        'skills': ['Design', 'UI/UX', 'Figma'],
        'experience_years': 4,
        'location': 'Abidjan, Côte d\'Ivoire',
        'rating': 4.9,
        'completed_projects': 22
    },
    {
        'first_name': 'Kofi',
        'last_name': 'Mensah',
        'email': 'kofi.mensah@email.com',
        'hourly_rate': 20.00,
        'description': 'Rédacteur web SEO spécialisé dans le contenu marketing. Création de contenu engageant et optimisé pour les moteurs de recherche.',
        'skills': ['Rédaction', 'SEO', 'Marketing Digital'],
        'experience_years': 3,
        'location': 'Accra, Ghana',
        'rating': 4.7,
        'completed_projects': 18
    },
    {
        'first_name': 'Aisha',
        'last_name': 'Omar',
        'email': 'aisha.omar@email.com',
        'hourly_rate': 35.00,
        'description': 'Développeuse mobile native iOS et Android. Expert en Swift, Kotlin et React Native.',
        'skills': ['Développement Mobile', 'iOS', 'Android'],
        'experience_years': 6,
        'location': 'Nairobi, Kenya',
        'rating': 4.9,
        'completed_projects': 28
    },
    {
        'first_name': 'Moussa',
        'last_name': 'Traoré',
        'email': 'moussa.traore@email.com',
        'hourly_rate': 22.00,
        'description': 'Graphiste freelance spécialisé dans l\'identité visuelle et le branding. Création de logos, chartes graphiques et supports marketing.',
        'skills': ['Graphisme', 'Branding', 'Illustration'],
        'experience_years': 4,
        'location': 'Bamako, Mali',
        'rating': 4.6,
        'completed_projects': 12
    },
    {
        'first_name': 'Zara',
        'last_name': 'Bello',
        'email': 'zara.bello@email.com',
        'hourly_rate': 28.00,
        'description': 'Traductrice professionnelle français-anglais-arabe. Spécialisée dans les documents techniques et commerciaux.',
        'skills': ['Traduction', 'Français', 'Anglais', 'Arabe'],
        'experience_years': 7,
        'location': 'Lagos, Nigeria',
        'rating': 4.8,
        'completed_projects': 35
    },
    {
        'first_name': 'Théo',
        'last_name': 'Kouassi',
        'email': 'theo.kouassi@email.com',
        'hourly_rate': 40.00,
        'description': 'Expert en marketing digital et stratégie de croissance. Spécialisé dans les campagnes publicitaires et l\'analyse de données.',
        'skills': ['Marketing Digital', 'Google Ads', 'Analytics'],
        'experience_years': 8,
        'location': 'Abidjan, Côte d\'Ivoire',
        'rating': 4.9,
        'completed_projects': 42
    },
    {
        'first_name': 'Mariam',
        'last_name': 'Keita',
        'email': 'mariam.keita@email.com',
        'hourly_rate': 25.00,
        'description': 'Monteuse vidéo et motion designer. Création de vidéos promotionnelles, publicités et contenus pour réseaux sociaux.',
        'skills': ['Vidéo', 'Motion Design', 'After Effects'],
        'experience_years': 5,
        'location': 'Conakry, Guinée',
        'rating': 4.7,
        'completed_projects': 19
    },
    {
        'first_name': 'David',
        'last_name': 'Eze',
        'email': 'david.eze@email.com',
        'hourly_rate': 32.00,
        'description': 'Ingénieur audio et producteur de musique. Spécialisé dans le mixage, mastering et production de podcasts.',
        'skills': ['Audio', 'Production', 'Podcast'],
        'experience_years': 6,
        'location': 'Lagos, Nigeria',
        'rating': 4.8,
        'completed_projects': 25
    },
    {
        'first_name': 'Sara',
        'last_name': 'Mekonnen',
        'email': 'sara.mekonnen@email.com',
        'hourly_rate': 18.00,
        'description': 'Rédactrice web polyvalente. Création de contenu pour blogs, sites web et réseaux sociaux.',
        'skills': ['Rédaction', 'Blog', 'Réseaux sociaux'],
        'experience_years': 2,
        'location': 'Addis Abeba, Éthiopie',
        'rating': 4.5,
        'completed_projects': 8
    }
]

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

print("Création des utilisateurs et freelances...")

# Créer les freelances
for i, data in enumerate(freelancer_data):
    # Créer l'utilisateur
    username = f"freelancer{i+1}"
    user = User.objects.create_user(
        username=username,
        email=data['email'],
        password='password123',
        first_name=data['first_name'],
        last_name=data['last_name']
    )
    
    # Créer le profil freelance
    freelancer = Freelancer.objects.create(
        user=user,
        hourly_rate=data['hourly_rate'],
        description=data['description'],
        skills=data['skills'],
        experience_years=data['experience_years'],
        location=data['location'],
        rating=data['rating'],
        total_reviews=random.randint(5, 50),
        completed_projects=data['completed_projects'],
        total_earnings=data['hourly_rate'] * data['completed_projects'] * 10,
        is_verified=random.choice([True, False]),
        is_featured=random.choice([True, False]),
        availability_status=random.choice(['available', 'busy', 'available'])
    )
    print(f"Freelance créé : {data['first_name']} {data['last_name']}")

print("\nCréation des clients et projets...")

# Créer les clients et projets
for i, data in enumerate(project_data):
    # Créer l'utilisateur client
    username = f"client{i+1}"
    user = User.objects.create_user(
        username=username,
        email=f"client{i+1}@email.com",
        password='password123',
        first_name=f"Client{i+1}",
        last_name="Test"
    )
    
    # Créer le profil client
    client = Client.objects.create(
        user=user,
        company_name=f"Entreprise {i+1}",
        company_description=f"Description de l'entreprise {i+1}",
        location=random.choice(['Dakar', 'Abidjan', 'Lagos', 'Nairobi', 'Accra']),
        is_verified=random.choice([True, False])
    )
    
    # Trouver la catégorie ou utiliser la première disponible
    try:
        category = Category.objects.get(name=data['category'])
    except Category.DoesNotExist:
        category = Category.objects.first()
    
    # Créer le projet
    from datetime import date, timedelta
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
print(f"   - {len(freelancer_data)} freelances créés")
print(f"   - {len(project_data)} projets créés")
print(f"   - {len(categories)} catégories disponibles")
