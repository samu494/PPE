from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.db.models import Avg, Count

# Import payment models to ensure they are registered with Django
from .payment_models import PaymentMethod, CryptoPayment, MobileMoneyPayment, PayPalPayment, PaymentGateway, PaymentTransaction

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom")
    description = models.TextField(verbose_name="Description")
    icon = models.CharField(max_length=50, default="ri-folder-line", verbose_name="Icône")
    freelancer_count = models.IntegerField(default=0, verbose_name="Nombre de freelances")
    project_count = models.IntegerField(default=0, verbose_name="Nombre de projets")
    color = models.CharField(max_length=7, default="#3b82f6", verbose_name="Couleur")
    is_featured = models.BooleanField(default=False, verbose_name="Mise en avant")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['-is_featured', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_projects', kwargs={'category_id': self.id})

class Freelancer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    profile_picture = models.ImageField(upload_to='freelancers/', null=True, blank=True, verbose_name="Photo de profil")
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Taux horaire (€)")
    description = models.TextField(default='', verbose_name="Description")
    skills = models.JSONField(default=list, verbose_name="Compétences")
    experience_years = models.IntegerField(default=0, verbose_name="Années d'expérience")
    education = models.TextField(blank=True, verbose_name="Formation")
    languages = models.JSONField(default=list, verbose_name="Langues")
    location = models.CharField(max_length=100, blank=True, verbose_name="Localisation")
    portfolio_link = models.URLField(blank=True, verbose_name="Lien portfolio")
    is_verified = models.BooleanField(default=False, verbose_name="Vérifié")
    is_featured = models.BooleanField(default=False, verbose_name="Mise en avant")
    availability_status = models.CharField(
        max_length=20,
        choices=[
            ('available', 'Disponible'),
            ('busy', 'Occupé'),
            ('unavailable', 'Indisponible'),
        ],
        default='available',
        verbose_name="Statut de disponibilité"
    )
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, verbose_name="Note moyenne")
    total_reviews = models.IntegerField(default=0, verbose_name="Nombre total d'avis")
    completed_projects = models.IntegerField(default=0, verbose_name="Projets terminés")
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Gains totaux")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Freelance"
        verbose_name_plural = "Freelances"

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.user.email}"

    def get_absolute_url(self):
        return reverse('freelancer_detail', kwargs={'freelancer_id': self.id})

    def calculate_rating(self):
        reviews = Review.objects.filter(freelancer=self)
        if reviews.exists():
            avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
            self.rating = round(avg_rating, 2)
            self.total_reviews = reviews.count()
            self.save()

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    company_name = models.CharField(max_length=100, blank=True, verbose_name="Nom de l'entreprise")
    company_description = models.TextField(blank=True, verbose_name="Description de l'entreprise")
    profile_picture = models.ImageField(upload_to='clients/', null=True, blank=True, verbose_name="Photo de profil")
    location = models.CharField(max_length=100, blank=True, verbose_name="Localisation")
    website = models.URLField(blank=True, verbose_name="Site web")
    is_verified = models.BooleanField(default=False, verbose_name="Vérifié")
    total_projects = models.IntegerField(default=0, verbose_name="Total des projets")
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Total dépensé")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.company_name or self.user.email}"

class Project(models.Model):
    STATUS_CHOICES = [
        ('open', 'Ouvert'),
        ('in_progress', 'En cours'),
        ('completed', 'Terminé'),
        ('cancelled', 'Annulé'),
        ('paused', 'En pause'),
    ]

    BUDGET_TYPE_CHOICES = [
        ('fixed', 'Budget fixe'),
        ('hourly', 'Taux horaire'),
        ('negotiable', 'Négociable'),
    ]

    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(verbose_name="Description")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Catégorie")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Client")
    budget_min = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Budget minimum (€)")
    budget_max = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Budget maximum (€)")
    budget_type = models.CharField(max_length=20, choices=BUDGET_TYPE_CHOICES, default='fixed', verbose_name="Type de budget")
    deadline = models.DateField(verbose_name="Date limite")
    required_skills = models.JSONField(default=list, verbose_name="Compétences requises")
    attachments = models.JSONField(default=list, verbose_name="Pièces jointes")
    additional_info = models.TextField(blank=True, verbose_name="Informations supplémentaires")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', verbose_name="Statut")
    is_featured = models.BooleanField(default=False, verbose_name="Mise en avant")
    is_urgent = models.BooleanField(default=False, verbose_name="Urgent")
    views_count = models.IntegerField(default=0, verbose_name="Nombre de vues")
    proposals_count = models.IntegerField(default=0, verbose_name="Nombre de propositions")
    selected_freelancer = models.ForeignKey(Freelancer, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Freelance sélectionné")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Projet"
        verbose_name_plural = "Projets"
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('project_detail', kwargs={'project_id': self.id})

    def get_budget_display(self):
        if self.budget_type == 'fixed':
            return f"{self.budget_min}€ - {self.budget_max}€"
        elif self.budget_type == 'hourly':
            return f"{self.budget_min}€/h - {self.budget_max}€/h"
        else:
            return "Négociable"

class Proposal(models.Model):
    STATUS_CHOICES = [
        ('pending_admin', 'En attente de validation admin'),
        ('pending', 'En attente'),
        ('accepted', 'Acceptée'),
        ('rejected', 'Refusée'),
        ('withdrawn', 'Retirée'),
    ]

    ADMIN_VALIDATION_CHOICES = [
        ('pending', 'En attente'),
        ('approved', 'Approuvée'),
        ('rejected', 'Rejetée'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="Projet")
    freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE, verbose_name="Freelance")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix proposé (€)")
    delivery_time = models.IntegerField(verbose_name="Délai de livraison (jours)")
    message = models.TextField(verbose_name="Message")
    attachments = models.JSONField(default=list, verbose_name="Pièces jointes")
    additional_info = models.TextField(blank=True, verbose_name="Informations supplémentaires")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_admin', verbose_name="Statut")
    is_featured = models.BooleanField(default=False, verbose_name="Mise en avant")
    admin_validation = models.CharField(max_length=20, choices=ADMIN_VALIDATION_CHOICES, default='pending', verbose_name="Validation admin")
    admin_comment = models.TextField(blank=True, verbose_name="Commentaire admin")
    validated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='validated_proposals', verbose_name="Validé par")
    validation_date = models.DateTimeField(null=True, blank=True, verbose_name="Date de validation")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Proposition"
        verbose_name_plural = "Propositions"
        ordering = ['-is_featured', '-created_at']
        unique_together = ['project', 'freelancer']

    def __str__(self):
        return f"{self.freelancer.user.get_full_name()} - {self.project.title}"
        
    def save(self, *args, **kwargs):
        # Si la proposition est validée par l'admin, mettre à jour le statut
        if self.admin_validation == 'approved' and self.status == 'pending_admin':
            self.status = 'pending'
        super().save(*args, **kwargs)

class Review(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="Projet")
    freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE, verbose_name="Freelance")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Client")
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="Note")
    comment = models.TextField(verbose_name="Commentaire")
    is_public = models.BooleanField(default=True, verbose_name="Public")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Avis"
        verbose_name_plural = "Avis"
        unique_together = ['project', 'freelancer', 'client']

    def __str__(self):
        return f"Avis de {self.client.user.get_full_name()} sur {self.freelancer.user.get_full_name()}"

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', verbose_name="Expéditeur")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', verbose_name="Destinataire")
    content = models.TextField(verbose_name="Contenu")
    is_read = models.BooleanField(default=False, verbose_name="Lu")
    attachments = models.JSONField(default=list, verbose_name="Pièces jointes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.get_full_name()} → {self.receiver.get_full_name()}"

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('project_proposal', 'Nouvelle proposition'),
        ('proposal_accepted', 'Proposition acceptée'),
        ('proposal_rejected', 'Proposition refusée'),
        ('project_awarded', 'Projet attribué'),
        ('project_completed', 'Projet terminé'),
        ('new_message', 'Nouveau message'),
        ('review_received', 'Nouvel avis'),
        ('payment_received', 'Paiement reçu'),
        ('system_alert', 'Alerte système'),
        ('project_update', 'Mise à jour projet'),
        ('milestone_reached', 'Étape atteinte'),
        ('deadline_reminder', 'Rappel échéance'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Destinataire")
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, verbose_name="Type")
    title = models.CharField(max_length=200, verbose_name="Titre")
    message = models.TextField(verbose_name="Message")
    related_object_id = models.IntegerField(null=True, blank=True, verbose_name="ID objet lié")
    related_object_type = models.CharField(max_length=50, blank=True, verbose_name="Type objet lié")
    is_read = models.BooleanField(default=False, verbose_name="Lu")
    is_important = models.BooleanField(default=False, verbose_name="Important")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.get_full_name()} - {self.title}"

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En cours'),
        ('completed', 'Terminé'),
        ('failed', 'Échoué'),
        ('refunded', 'Remboursé'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('card', 'Carte bancaire'),
        ('paypal', 'PayPal'),
        ('mobile_money', 'Mobile Money'),
        ('bank_transfer', 'Virement bancaire'),
        ('crypto', 'Cryptomonnaie'),
        ('cash', 'Espèces'),
        ('check', 'Chèque'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="Projet")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Client")
    freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE, verbose_name="Freelance")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant (€)")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, verbose_name="Méthode de paiement")
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending', verbose_name="Statut")
    transaction_id = models.CharField(max_length=100, blank=True, verbose_name="ID transaction")
    description = models.TextField(blank=True, verbose_name="Description")
    currency = models.CharField(max_length=3, default='EUR', verbose_name="Devise")
    processing_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Frais de traitement")
    gateway_response = models.JSONField(default=dict, verbose_name="Réponse de la passerelle")
    payment_gateway = models.ForeignKey('PaymentGateway', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Passerelle de paiement")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ['-created_at']

    def __str__(self):
        return f"Paiement {self.transaction_id} - {self.amount}€"

class Milestone(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('in_progress', 'En cours'),
        ('completed', 'Terminé'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="Projet")
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(verbose_name="Description")
    due_date = models.DateField(verbose_name="Date d'échéance")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant (€)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    deliverables = models.JSONField(default=list, verbose_name="Livrables")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Étape"
        verbose_name_plural = "Étapes"
        ordering = ['due_date']

    def __str__(self):
        return f"{self.project.title} - {self.title}"

class Dispute(models.Model):
    DISPUTE_STATUS_CHOICES = [
        ('open', 'Ouvert'),
        ('under_review', 'En cours d\'examen'),
        ('resolved', 'Résolu'),
        ('closed', 'Fermé'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="Projet")
    initiator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Initiateur")
    reason = models.CharField(max_length=200, verbose_name="Raison")
    description = models.TextField(verbose_name="Description")
    evidence = models.JSONField(default=list, verbose_name="Preuves")
    status = models.CharField(max_length=20, choices=DISPUTE_STATUS_CHOICES, default='open', verbose_name="Statut")
    resolution = models.TextField(blank=True, verbose_name="Résolution")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Litige"
        verbose_name_plural = "Litiges"
        ordering = ['-created_at']

    def __str__(self):
        return f"Litige - {self.project.title}"

class SupportTicket(models.Model):
    TICKET_STATUS_CHOICES = [
        ('open', 'Ouvert'),
        ('in_progress', 'En cours de traitement'),
        ('waiting', 'En attente de réponse'),
        ('resolved', 'Résolu'),
        ('closed', 'Fermé'),
    ]
    
    TICKET_PRIORITY_CHOICES = [
        ('low', 'Basse'),
        ('medium', 'Moyenne'),
        ('high', 'Haute'),
        ('urgent', 'Urgente'),
    ]
    
    TICKET_TYPE_CHOICES = [
        ('technical', 'Problème technique'),
        ('billing', 'Facturation'),
        ('account', 'Compte utilisateur'),
        ('project', 'Problème de projet'),
        ('payment', 'Problème de paiement'),
        ('other', 'Autre'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    subject = models.CharField(max_length=200, verbose_name="Sujet")
    description = models.TextField(verbose_name="Description")
    ticket_type = models.CharField(max_length=20, choices=TICKET_TYPE_CHOICES, default='other', verbose_name="Type de ticket")
    priority = models.CharField(max_length=20, choices=TICKET_PRIORITY_CHOICES, default='medium', verbose_name="Priorité")
    status = models.CharField(max_length=20, choices=TICKET_STATUS_CHOICES, default='open', verbose_name="Statut")
    attachments = models.JSONField(default=list, verbose_name="Pièces jointes")
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets', verbose_name="Assigné à")
    related_project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Projet concerné")
    resolution = models.TextField(blank=True, verbose_name="Résolution")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Ticket de support"
        verbose_name_plural = "Tickets de support"
        ordering = ['-priority', '-created_at']
    
    def __str__(self):
        return f"Ticket #{self.id} - {self.subject}"

class TicketResponse(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='responses', verbose_name="Ticket")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    message = models.TextField(verbose_name="Message")
    attachments = models.JSONField(default=list, verbose_name="Pièces jointes")
    is_staff_response = models.BooleanField(default=False, verbose_name="Réponse du staff")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Réponse de ticket"
        verbose_name_plural = "Réponses de tickets"
        ordering = ['created_at']
    
    def __str__(self):
        return f"Réponse de {self.user.get_full_name()} - Ticket #{self.ticket.id}"

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Catégorie")
    icon = models.CharField(max_length=50, default="ri-code-line", verbose_name="Icône")
    is_popular = models.BooleanField(default=False, verbose_name="Populaire")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Compétence"
        verbose_name_plural = "Compétences"
        ordering = ['-is_popular', 'name']

    def __str__(self):
        return self.name