from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import uuid

class PaymentMethod(models.Model):
    """Modèle pour les méthodes de paiement disponibles"""
    
    PAYMENT_TYPES = [
        ('card', 'Carte bancaire'),
        ('paypal', 'PayPal'),
        ('mobile_money', 'Mobile Money'),
        ('bank_transfer', 'Virement bancaire'),
        ('crypto', 'Cryptomonnaie'),
        ('cash', 'Espèces'),
        ('check', 'Chèque'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('inactive', 'Inactif'),
        ('maintenance', 'En maintenance'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Nom")
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES, verbose_name="Type de paiement")
    description = models.TextField(blank=True, verbose_name="Description")
    icon = models.CharField(max_length=50, default="ri-bank-card-line", verbose_name="Icône")
    is_available = models.BooleanField(default=True, verbose_name="Disponible")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Statut")
    processing_fee = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="Frais de traitement (%)")
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Montant minimum")
    max_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Montant maximum")
    supported_countries = models.JSONField(default=list, verbose_name="Pays supportés")
    api_config = models.JSONField(default=dict, verbose_name="Configuration API")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Méthode de paiement"
        verbose_name_plural = "Méthodes de paiement"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def is_available_for_country(self, country_code):
        """Vérifie si la méthode est disponible pour un pays"""
        return country_code in self.supported_countries
    
    def calculate_fee(self, amount):
        """Calcule les frais de traitement"""
        return (amount * self.processing_fee) / 100

class CryptoPayment(models.Model):
    """Modèle pour les paiements en cryptomonnaie"""
    
    CRYPTO_TYPES = [
        ('bitcoin', 'Bitcoin (BTC)'),
        ('ethereum', 'Ethereum (ETH)'),
        ('litecoin', 'Litecoin (LTC)'),
        ('bitcoin_cash', 'Bitcoin Cash (BCH)'),
        ('ripple', 'Ripple (XRP)'),
        ('cardano', 'Cardano (ADA)'),
        ('polkadot', 'Polkadot (DOT)'),
        ('chainlink', 'Chainlink (LINK)'),
        ('stellar', 'Stellar (XLM)'),
        ('usdt', 'Tether (USDT)'),
        ('usdc', 'USD Coin (USDC)'),
        ('dai', 'Dai (DAI)'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmé'),
        ('failed', 'Échoué'),
        ('expired', 'Expiré'),
    ]
    
    payment = models.OneToOneField('Payment', on_delete=models.CASCADE, verbose_name="Paiement")
    crypto_type = models.CharField(max_length=20, choices=CRYPTO_TYPES, verbose_name="Type de crypto")
    crypto_amount = models.DecimalField(max_digits=20, decimal_places=8, verbose_name="Montant en crypto")
    exchange_rate = models.DecimalField(max_digits=20, decimal_places=8, verbose_name="Taux de change")
    wallet_address = models.CharField(max_length=100, verbose_name="Adresse de portefeuille")
    transaction_hash = models.CharField(max_length=100, blank=True, verbose_name="Hash de transaction")
    block_height = models.IntegerField(null=True, blank=True, verbose_name="Hauteur de bloc")
    confirmations = models.IntegerField(default=0, verbose_name="Confirmations")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    expires_at = models.DateTimeField(verbose_name="Expire à")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Paiement crypto"
        verbose_name_plural = "Paiements crypto"
    
    def __str__(self):
        return f"{self.crypto_type} - {self.crypto_amount}"
    
    def is_expired(self):
        """Vérifie si le paiement a expiré"""
        return timezone.now() > self.expires_at
    
    def get_confirmation_status(self):
        """Retourne le statut de confirmation"""
        if self.crypto_type == 'bitcoin':
            return 'confirmed' if self.confirmations >= 6 else 'pending'
        elif self.crypto_type == 'ethereum':
            return 'confirmed' if self.confirmations >= 12 else 'pending'
        else:
            return 'confirmed' if self.confirmations >= 3 else 'pending'

class MobileMoneyPayment(models.Model):
    """Modèle pour les paiements Mobile Money"""
    
    PROVIDER_CHOICES = [
        ('mpesa', 'M-Pesa (Kenya)'),
        ('airtel_money', 'Airtel Money'),
        ('mtn_momo', 'MTN Mobile Money'),
        ('orange_money', 'Orange Money'),
        ('vodafone_cash', 'Vodafone Cash'),
        ('tigo_pesa', 'Tigo Pesa'),
        ('ecocash', 'EcoCash (Zimbabwe)'),
        ('mobikwik', 'MobiKwik (Inde)'),
        ('paytm', 'Paytm (Inde)'),
        ('phonepe', 'PhonePe (Inde)'),
        ('gpay', 'Google Pay'),
        ('apple_pay', 'Apple Pay'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En cours'),
        ('completed', 'Terminé'),
        ('failed', 'Échoué'),
        ('cancelled', 'Annulé'),
    ]
    
    payment = models.OneToOneField('Payment', on_delete=models.CASCADE, verbose_name="Paiement")
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, verbose_name="Fournisseur")
    phone_number = models.CharField(max_length=20, verbose_name="Numéro de téléphone")
    transaction_id = models.CharField(max_length=100, blank=True, verbose_name="ID de transaction")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Paiement Mobile Money"
        verbose_name_plural = "Paiements Mobile Money"
    
    def __str__(self):
        return f"{self.provider} - {self.phone_number}"

class PayPalPayment(models.Model):
    """Modèle pour les paiements PayPal"""
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('completed', 'Terminé'),
        ('failed', 'Échoué'),
        ('cancelled', 'Annulé'),
        ('refunded', 'Remboursé'),
    ]
    
    payment = models.OneToOneField('Payment', on_delete=models.CASCADE, verbose_name="Paiement")
    paypal_order_id = models.CharField(max_length=100, verbose_name="ID commande PayPal")
    paypal_payment_id = models.CharField(max_length=100, blank=True, verbose_name="ID paiement PayPal")
    payer_id = models.CharField(max_length=100, blank=True, verbose_name="ID payeur")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Paiement PayPal"
        verbose_name_plural = "Paiements PayPal"
    
    def __str__(self):
        return f"PayPal - {self.paypal_order_id}"

class PaymentGateway(models.Model):
    """Modèle pour les passerelles de paiement"""
    
    GATEWAY_TYPES = [
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('razorpay', 'Razorpay'),
        ('flutterwave', 'Flutterwave'),
        ('paystack', 'Paystack'),
        ('mpesa', 'M-Pesa'),
        ('crypto', 'Cryptomonnaie'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('inactive', 'Inactif'),
        ('test', 'Mode test'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Nom")
    gateway_type = models.CharField(max_length=20, choices=GATEWAY_TYPES, verbose_name="Type de passerelle")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='test', verbose_name="Statut")
    api_key = models.CharField(max_length=255, verbose_name="Clé API")
    secret_key = models.CharField(max_length=255, verbose_name="Clé secrète")
    webhook_url = models.URLField(blank=True, verbose_name="URL webhook")
    supported_currencies = models.JSONField(default=list, verbose_name="Devises supportées")
    supported_countries = models.JSONField(default=list, verbose_name="Pays supportés")
    processing_fee = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="Frais (%)")
    fixed_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Frais fixes")
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Montant minimum")
    max_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Montant maximum")
    config = models.JSONField(default=dict, verbose_name="Configuration")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Passerelle de paiement"
        verbose_name_plural = "Passerelles de paiement"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.gateway_type})"
    
    def calculate_fees(self, amount):
        """Calcule les frais totaux"""
        percentage_fee = (amount * self.processing_fee) / 100
        return percentage_fee + self.fixed_fee
    
    def is_available_for_country(self, country_code):
        """Vérifie si la passerelle est disponible pour un pays"""
        return country_code in self.supported_countries
    
    def is_available_for_currency(self, currency_code):
        """Vérifie si la passerelle supporte une devise"""
        return currency_code in self.supported_currencies

class PaymentTransaction(models.Model):
    """Modèle pour tracer toutes les transactions de paiement"""
    
    TRANSACTION_TYPES = [
        ('payment', 'Paiement'),
        ('refund', 'Remboursement'),
        ('chargeback', 'Contestation'),
        ('fee', 'Frais'),
        ('adjustment', 'Ajustement'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En cours'),
        ('completed', 'Terminé'),
        ('failed', 'Échoué'),
        ('cancelled', 'Annulé'),
        ('refunded', 'Remboursé'),
    ]
    
    transaction_id = models.CharField(max_length=100, unique=True, verbose_name="ID de transaction")
    payment = models.ForeignKey('Payment', on_delete=models.CASCADE, verbose_name="Paiement")
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, verbose_name="Type de transaction")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant")
    currency = models.CharField(max_length=3, default='EUR', verbose_name="Devise")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    gateway_response = models.JSONField(default=dict, verbose_name="Réponse de la passerelle")
    error_message = models.TextField(blank=True, verbose_name="Message d'erreur")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Transaction de paiement"
        verbose_name_plural = "Transactions de paiement"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.transaction_id} - {self.amount} {self.currency}"
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = f"TXN-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

