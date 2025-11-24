#!/usr/bin/env python
"""
Script pour initialiser les données de paiement FreeAfrique
"""

import os
import sys
import django
from decimal import Decimal

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freeafrique.settings')
django.setup()

from main.payment_models import PaymentMethod, PaymentGateway

def setup_payment_methods():
    """Configure les méthodes de paiement disponibles"""
    print("🔧 Configuration des méthodes de paiement...")
    
    methods_data = [
        {
            'name': 'Carte bancaire',
            'payment_type': 'card',
            'description': 'Paiement par carte bancaire (Visa, Mastercard, American Express)',
            'icon': 'ri-bank-card-line',
            'processing_fee': Decimal('2.90'),
            'min_amount': Decimal('1.00'),
            'supported_countries': ['FR', 'US', 'GB', 'DE', 'IT', 'ES', 'CA', 'AU', 'JP', 'BR', 'IN', 'CN'],
        },
        {
            'name': 'PayPal',
            'payment_type': 'paypal',
            'description': 'Paiement via PayPal (compte ou carte)',
            'icon': 'ri-paypal-line',
            'processing_fee': Decimal('3.50'),
            'min_amount': Decimal('1.00'),
            'supported_countries': ['FR', 'US', 'GB', 'DE', 'IT', 'ES', 'CA', 'AU', 'JP', 'BR', 'IN', 'CN', 'MX', 'AR', 'CL', 'CO', 'PE'],
        },
        {
            'name': 'Mobile Money',
            'payment_type': 'mobile_money',
            'description': 'Paiement via Mobile Money (M-Pesa, Orange Money, MTN MoMo)',
            'icon': 'ri-smartphone-line',
            'processing_fee': Decimal('1.50'),
            'min_amount': Decimal('0.50'),
            'supported_countries': ['KE', 'TZ', 'UG', 'RW', 'BI', 'CD', 'CG', 'CM', 'CI', 'SN', 'ML', 'BF', 'NE', 'TD', 'MG', 'MU', 'ZW', 'ZM', 'MW', 'IN', 'BD', 'PK', 'LK', 'NP'],
        },
        {
            'name': 'Cryptomonnaie',
            'payment_type': 'crypto',
            'description': 'Paiement en cryptomonnaie (Bitcoin, Ethereum, USDT, etc.)',
            'icon': 'ri-bit-coin-line',
            'processing_fee': Decimal('1.00'),
            'min_amount': Decimal('10.00'),
            'supported_countries': ['FR', 'US', 'GB', 'DE', 'IT', 'ES', 'CA', 'AU', 'JP', 'BR', 'IN', 'CN', 'KR', 'SG', 'HK', 'TW', 'MY', 'TH', 'VN', 'ID', 'PH'],
        },
        {
            'name': 'Virement bancaire',
            'payment_type': 'bank_transfer',
            'description': 'Virement bancaire SEPA',
            'icon': 'ri-bank-line',
            'processing_fee': Decimal('0.00'),
            'min_amount': Decimal('10.00'),
            'supported_countries': ['FR', 'DE', 'IT', 'ES', 'NL', 'BE', 'AT', 'PT', 'IE', 'FI', 'SE', 'DK', 'NO', 'CH', 'PL', 'CZ', 'HU', 'RO', 'BG', 'HR', 'SI', 'SK', 'LT', 'LV', 'EE', 'LU', 'MT', 'CY'],
        },
        {
            'name': 'Espèces',
            'payment_type': 'cash',
            'description': 'Paiement en espèces (sur demande)',
            'icon': 'ri-money-dollar-circle-line',
            'processing_fee': Decimal('0.00'),
            'min_amount': Decimal('5.00'),
            'supported_countries': ['FR', 'DE', 'IT', 'ES', 'BE', 'CH', 'CA', 'AU', 'JP', 'KR', 'SG', 'HK', 'TW'],
        },
    ]
    
    for method_data in methods_data:
        method, created = PaymentMethod.objects.get_or_create(
            name=method_data['name'],
            defaults=method_data
        )
        
        if created:
            print(f"✅ Méthode créée: {method.name}")
        else:
            print(f"ℹ️ Méthode existante: {method.name}")
    
    print("✅ Configuration des méthodes de paiement terminée\n")

def setup_payment_gateways():
    """Configure les passerelles de paiement"""
    print("🔧 Configuration des passerelles de paiement...")
    
    gateways_data = [
        {
            'name': 'Stripe',
            'gateway_type': 'stripe',
            'api_key': 'pk_test_...',  # À remplacer par vos vraies clés
            'secret_key': 'sk_test_...',
            'supported_currencies': ['EUR', 'USD', 'GBP', 'CAD', 'AUD', 'JPY'],
            'supported_countries': ['FR', 'US', 'GB', 'DE', 'IT', 'ES', 'CA', 'AU', 'JP'],
            'processing_fee': Decimal('2.90'),
            'fixed_fee': Decimal('0.30'),
            'min_amount': Decimal('0.50'),
        },
        {
            'name': 'PayPal',
            'gateway_type': 'paypal',
            'api_key': 'client_id_...',  # À remplacer par vos vraies clés
            'secret_key': 'secret_...',
            'supported_currencies': ['EUR', 'USD', 'GBP', 'CAD', 'AUD', 'JPY', 'BRL', 'MXN', 'ARS', 'CLP', 'COP', 'PEN'],
            'supported_countries': ['FR', 'US', 'GB', 'DE', 'IT', 'ES', 'CA', 'AU', 'JP', 'BR', 'MX', 'AR', 'CL', 'CO', 'PE'],
            'processing_fee': Decimal('3.50'),
            'fixed_fee': Decimal('0.35'),
            'min_amount': Decimal('1.00'),
        },
        {
            'name': 'M-Pesa',
            'gateway_type': 'mpesa',
            'api_key': 'consumer_key_...',  # À remplacer par vos vraies clés
            'secret_key': 'consumer_secret_...',
            'supported_currencies': ['KES', 'TZS', 'UGX', 'RWF', 'BIF', 'CDF', 'XAF'],
            'supported_countries': ['KE', 'TZ', 'UG', 'RW', 'BI', 'CD', 'CG', 'CM', 'CI', 'SN', 'ML', 'BF', 'NE', 'TD'],
            'processing_fee': Decimal('1.50'),
            'fixed_fee': Decimal('0.00'),
            'min_amount': Decimal('0.50'),
        },
        {
            'name': 'Flutterwave',
            'gateway_type': 'flutterwave',
            'api_key': 'FLWPUBK_...',  # À remplacer par vos vraies clés
            'secret_key': 'FLWSECK_...',
            'supported_currencies': ['NGN', 'GHS', 'KES', 'UGX', 'TZS', 'ZAR', 'XAF', 'XOF'],
            'supported_countries': ['NG', 'GH', 'KE', 'UG', 'TZ', 'ZA', 'CM', 'CI', 'SN', 'ML', 'BF', 'NE', 'TD'],
            'processing_fee': Decimal('1.40'),
            'fixed_fee': Decimal('0.00'),
            'min_amount': Decimal('0.50'),
        },
        {
            'name': 'Paystack',
            'gateway_type': 'paystack',
            'api_key': 'pk_test_...',  # À remplacer par vos vraies clés
            'secret_key': 'sk_test_...',
            'supported_currencies': ['NGN', 'GHS', 'ZAR', 'USD'],
            'supported_countries': ['NG', 'GH', 'ZA'],
            'processing_fee': Decimal('1.50'),
            'fixed_fee': Decimal('0.00'),
            'min_amount': Decimal('0.50'),
        },
        {
            'name': 'Crypto Gateway',
            'gateway_type': 'crypto',
            'api_key': 'api_key_...',  # À remplacer par vos vraies clés
            'secret_key': 'api_secret_...',
            'supported_currencies': ['BTC', 'ETH', 'LTC', 'BCH', 'XRP', 'ADA', 'DOT', 'LINK', 'XLM', 'USDT', 'USDC', 'DAI'],
            'supported_countries': ['FR', 'US', 'GB', 'DE', 'IT', 'ES', 'CA', 'AU', 'JP', 'BR', 'IN', 'CN', 'KR', 'SG', 'HK', 'TW', 'MY', 'TH', 'VN', 'ID', 'PH'],
            'processing_fee': Decimal('1.00'),
            'fixed_fee': Decimal('0.00'),
            'min_amount': Decimal('10.00'),
        },
    ]
    
    for gateway_data in gateways_data:
        gateway, created = PaymentGateway.objects.get_or_create(
            name=gateway_data['name'],
            defaults=gateway_data
        )
        
        if created:
            print(f"✅ Passerelle créée: {gateway.name}")
        else:
            print(f"ℹ️ Passerelle existante: {gateway.name}")
    
    print("✅ Configuration des passerelles de paiement terminée\n")

def setup_country_specific_methods():
    """Configure les méthodes spécifiques par pays"""
    print("🔧 Configuration des méthodes par pays...")
    
    # Méthodes spécifiques à l'Afrique
    african_methods = [
        {
            'name': 'M-Pesa Kenya',
            'payment_type': 'mobile_money',
            'description': 'Paiement via M-Pesa au Kenya',
            'icon': 'ri-smartphone-line',
            'processing_fee': Decimal('1.50'),
            'min_amount': Decimal('0.50'),
            'supported_countries': ['KE'],
        },
        {
            'name': 'Orange Money',
            'payment_type': 'mobile_money',
            'description': 'Paiement via Orange Money',
            'icon': 'ri-smartphone-line',
            'processing_fee': Decimal('1.50'),
            'min_amount': Decimal('0.50'),
            'supported_countries': ['CI', 'SN', 'ML', 'BF', 'NE', 'TD', 'MG', 'MU'],
        },
        {
            'name': 'MTN Mobile Money',
            'payment_type': 'mobile_money',
            'description': 'Paiement via MTN Mobile Money',
            'icon': 'ri-smartphone-line',
            'processing_fee': Decimal('1.50'),
            'min_amount': Decimal('0.50'),
            'supported_countries': ['GH', 'UG', 'RW', 'BI', 'CD', 'CG', 'CM'],
        },
    ]
    
    for method_data in african_methods:
        method, created = PaymentMethod.objects.get_or_create(
            name=method_data['name'],
            defaults=method_data
        )
        
        if created:
            print(f"✅ Méthode africaine créée: {method.name}")
        else:
            print(f"ℹ️ Méthode africaine existante: {method.name}")
    
    # Méthodes spécifiques à l'Asie
    asian_methods = [
        {
            'name': 'Paytm',
            'payment_type': 'mobile_money',
            'description': 'Paiement via Paytm en Inde',
            'icon': 'ri-smartphone-line',
            'processing_fee': Decimal('1.50'),
            'min_amount': Decimal('0.50'),
            'supported_countries': ['IN'],
        },
        {
            'name': 'PhonePe',
            'payment_type': 'mobile_money',
            'description': 'Paiement via PhonePe en Inde',
            'icon': 'ri-smartphone-line',
            'processing_fee': Decimal('1.50'),
            'min_amount': Decimal('0.50'),
            'supported_countries': ['IN'],
        },
        {
            'name': 'MobiKwik',
            'payment_type': 'mobile_money',
            'description': 'Paiement via MobiKwik en Inde',
            'icon': 'ri-smartphone-line',
            'processing_fee': Decimal('1.50'),
            'min_amount': Decimal('0.50'),
            'supported_countries': ['IN'],
        },
    ]
    
    for method_data in asian_methods:
        method, created = PaymentMethod.objects.get_or_create(
            name=method_data['name'],
            defaults=method_data
        )
        
        if created:
            print(f"✅ Méthode asiatique créée: {method.name}")
        else:
            print(f"ℹ️ Méthode asiatique existante: {method.name}")
    
    print("✅ Configuration des méthodes par pays terminée\n")

def main():
    """Fonction principale"""
    print("🚀 Configuration du système de paiement FreeAfrique...\n")
    
    try:
        setup_payment_methods()
        setup_payment_gateways()
        setup_country_specific_methods()
        
        print("🎉 Configuration terminée avec succès !")
        print("\n📋 Récapitulatif:")
        print(f"   • {PaymentMethod.objects.count()} méthodes de paiement configurées")
        print(f"   • {PaymentGateway.objects.count()} passerelles configurées")
        print("\n⚠️ N'oubliez pas de:")
        print("   • Remplacer les clés API par vos vraies clés")
        print("   • Configurer les webhooks pour les notifications")
        print("   • Tester chaque méthode de paiement")
        print("   • Vérifier la conformité réglementaire")
        
    except Exception as e:
        print(f"❌ Erreur lors de la configuration: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

