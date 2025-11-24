from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings
import json
from decimal import Decimal
import uuid

from .models import Payment, Project, Client, Freelancer, Notification
from .payment_models import (
    PaymentMethod, CryptoPayment, MobileMoneyPayment, 
    PayPalPayment, PaymentGateway, PaymentTransaction
)

@login_required
def payment_methods(request):
    """Affiche les méthodes de paiement disponibles"""
    methods = PaymentMethod.objects.filter(is_available=True, status='active')
    
    # Filtrer par pays si nécessaire
    user_country = getattr(request.user, 'country', 'FR')
    available_methods = []
    
    for method in methods:
        if method.is_available_for_country(user_country):
            available_methods.append(method)
    
    return render(request, 'payment/methods.html', {
        'payment_methods': available_methods
    })

@login_required
def process_payment(request, project_id):
    """Traite un paiement"""
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        amount = Decimal(request.POST.get('amount', 0))
        
        # Vérifier que l'utilisateur est le client du projet
        if not hasattr(request.user, 'client') or project.client != request.user.client:
            messages.error(request, 'Vous n\'êtes pas autorisé à payer ce projet')
            return redirect('project_detail', project_id=project_id)
        
        # Créer le paiement
        payment = Payment.objects.create(
            project=project,
            client=request.user.client,
            freelancer=project.selected_freelancer,
            amount=amount,
            payment_method=payment_method,
            status='pending'
        )
        
        # Rediriger vers la méthode de paiement appropriée
        if payment_method == 'crypto':
            return redirect('crypto_payment', payment_id=payment.id)
        elif payment_method == 'mobile_money':
            return redirect('mobile_money_payment', payment_id=payment.id)
        elif payment_method == 'paypal':
            return redirect('paypal_payment', payment_id=payment.id)
        elif payment_method == 'card':
            return redirect('card_payment', payment_id=payment.id)
        else:
            return redirect('bank_transfer_payment', payment_id=payment.id)
    
    return render(request, 'payment/process.html', {
        'project': project
    })

@login_required
def crypto_payment(request, payment_id):
    """Gère les paiements en cryptomonnaie"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.method == 'POST':
        crypto_type = request.POST.get('crypto_type')
        
        # Simuler un taux de change (en production, utiliser une API)
        exchange_rates = {
            'bitcoin': 45000.00,
            'ethereum': 3000.00,
            'litecoin': 150.00,
            'usdt': 1.00,
            'usdc': 1.00,
        }
        
        exchange_rate = exchange_rates.get(crypto_type, 1.00)
        crypto_amount = payment.amount / exchange_rate
        
        # Créer le paiement crypto
        crypto_payment = CryptoPayment.objects.create(
            payment=payment,
            crypto_type=crypto_type,
            crypto_amount=crypto_amount,
            exchange_rate=exchange_rate,
            wallet_address=generate_wallet_address(crypto_type),
            expires_at=timezone.now() + timezone.timedelta(hours=24)
        )
        
        return render(request, 'payment/crypto_details.html', {
            'payment': payment,
            'crypto_payment': crypto_payment
        })
    
    return render(request, 'payment/crypto_form.html', {
        'payment': payment
    })

@login_required
def mobile_money_payment(request, payment_id):
    """Gère les paiements Mobile Money"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.method == 'POST':
        provider = request.POST.get('provider')
        phone_number = request.POST.get('phone_number')
        
        # Créer le paiement Mobile Money
        mobile_payment = MobileMoneyPayment.objects.create(
            payment=payment,
            provider=provider,
            phone_number=phone_number
        )
        
        # Simuler l'envoi du code USSD/SMS
        # En production, intégrer avec l'API du fournisseur
        ussd_code = generate_ussd_code(provider, payment.amount)
        
        return render(request, 'payment/mobile_money_details.html', {
            'payment': payment,
            'mobile_payment': mobile_payment,
            'ussd_code': ussd_code
        })
    
    return render(request, 'payment/mobile_money_form.html', {
        'payment': payment
    })

@login_required
def paypal_payment(request, payment_id):
    """Gère les paiements PayPal"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.method == 'POST':
        # En production, intégrer avec l'API PayPal
        paypal_order_id = f"PAYPAL-{uuid.uuid4().hex[:8].upper()}"
        
        paypal_payment = PayPalPayment.objects.create(
            payment=payment,
            paypal_order_id=paypal_order_id
        )
        
        # Rediriger vers PayPal (en production)
        paypal_url = f"https://www.paypal.com/pay/{paypal_order_id}"
        
        return render(request, 'payment/paypal_redirect.html', {
            'payment': payment,
            'paypal_payment': paypal_payment,
            'paypal_url': paypal_url
        })
    
    return render(request, 'payment/paypal_form.html', {
        'payment': payment
    })

@login_required
def card_payment(request, payment_id):
    """Gère les paiements par carte bancaire"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.method == 'POST':
        # En production, intégrer avec Stripe ou autre passerelle
        card_number = request.POST.get('card_number')
        expiry = request.POST.get('expiry')
        cvv = request.POST.get('cvv')
        
        # Simuler le traitement
        payment.status = 'completed'
        payment.transaction_id = f"CARD-{uuid.uuid4().hex[:8].upper()}"
        payment.save()
        
        messages.success(request, 'Paiement traité avec succès')
        return redirect('payment_success', payment_id=payment.id)
    
    return render(request, 'payment/card_form.html', {
        'payment': payment
    })

@login_required
def bank_transfer_payment(request, payment_id):
    """Gère les virements bancaires"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.method == 'POST':
        # Générer les informations de virement
        bank_info = {
            'bank_name': 'Banque FreeAfrique',
            'account_number': 'FR76 1234 5678 9012 3456 7890 123',
            'swift_code': 'FRAFPP123',
            'reference': f"PROJ-{payment.project.id}-{payment.id}"
        }
        
        payment.status = 'pending'
        payment.save()
        
        return render(request, 'payment/bank_transfer_details.html', {
            'payment': payment,
            'bank_info': bank_info
        })
    
    return render(request, 'payment/bank_transfer_form.html', {
        'payment': payment
    })

@login_required
def payment_success(request, payment_id):
    """Page de succès de paiement"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    return render(request, 'payment/success.html', {
        'payment': payment
    })

@login_required
def payment_failed(request, payment_id):
    """Page d'échec de paiement"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    return render(request, 'payment/failed.html', {
        'payment': payment
    })

@csrf_exempt
def payment_webhook(request):
    """Webhook pour recevoir les notifications de paiement"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Traiter selon le type de webhook
            if 'paypal' in request.path:
                return handle_paypal_webhook(data)
            elif 'stripe' in request.path:
                return handle_stripe_webhook(data)
            elif 'mobile_money' in request.path:
                return handle_mobile_money_webhook(data)
            elif 'crypto' in request.path:
                return handle_crypto_webhook(data)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def validate_payment_api(request, payment_id):
    """API JSON pour que le client valide un paiement en attente"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    try:
        payment = Payment.objects.get(id=payment_id, client=request.user.client)
    except (Payment.DoesNotExist, AttributeError):
        return JsonResponse({'success': False, 'error': 'Paiement introuvable'}, status=404)
    
    if payment.status not in ['pending', 'processing']:
        return JsonResponse({'success': False, 'error': 'Paiement déjà traité'}, status=400)
    
    payment.status = 'completed'
    payment.save()
    
    # Notification pour le freelance
    try:
        Notification.objects.create(
            recipient=payment.freelancer.user,
            notification_type='payment_received',
            title='Paiement validé',
            message=f'Le paiement de {payment.amount}€ pour le projet "{payment.project.title}" a été validé.',
            related_object_id=payment.id,
            related_object_type='Payment'
        )
    except Exception:
        pass
    
    return JsonResponse({'success': True})

@login_required
def reject_payment_api(request, payment_id):
    """API JSON pour que le client rejette un paiement en attente"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    try:
        payment = Payment.objects.get(id=payment_id, client=request.user.client)
    except (Payment.DoesNotExist, AttributeError):
        return JsonResponse({'success': False, 'error': 'Paiement introuvable'}, status=404)
    
    if payment.status not in ['pending', 'processing']:
        return JsonResponse({'success': False, 'error': 'Paiement déjà traité'}, status=400)
    
    payment.status = 'failed'
    payment.save()
    
    return JsonResponse({'success': True})

# Handlers

def handle_paypal_webhook(data):
    """Traite les webhooks PayPal"""
    # En production, vérifier la signature
    payment_id = data.get('payment_id')
    status = data.get('status')
    
    try:
        paypal_payment = PayPalPayment.objects.get(paypal_payment_id=payment_id)
        payment = paypal_payment.payment
        
        if status == 'completed':
            payment.status = 'completed'
            payment.save()
        
        return JsonResponse({'status': 'success'})
    except PayPalPayment.DoesNotExist:
        return JsonResponse({'error': 'Payment not found'}, status=404)

def handle_stripe_webhook(data):
    """Traite les webhooks Stripe"""
    # En production, vérifier la signature
    return JsonResponse({'status': 'success'})

def handle_mobile_money_webhook(data):
    """Traite les webhooks Mobile Money"""
    # En production, traiter selon le fournisseur
    return JsonResponse({'status': 'success'})

def handle_crypto_webhook(data):
    """Traite les webhooks crypto"""
    # En production, vérifier la transaction sur la blockchain
    return JsonResponse({'status': 'success'})

# Fonctions utilitaires
def generate_wallet_address(crypto_type):
    """Génère une adresse de portefeuille (simulation)"""
    # En production, utiliser une vraie API de génération d'adresses
    prefixes = {
        'bitcoin': 'bc1',
        'ethereum': '0x',
        'litecoin': 'ltc1',
        'usdt': '0x',
    }
    
    prefix = prefixes.get(crypto_type, '0x')
    return f"{prefix}{uuid.uuid4().hex[:40]}"

def generate_ussd_code(provider, amount):
    """Génère un code USSD (simulation)"""
    codes = {
        'mpesa': f"*144*1*{amount}#",
        'airtel_money': f"*126*1*{amount}#",
        'mtn_momo': f"*165*1*{amount}#",
        'orange_money': f"*144*1*{amount}#",
    }
    
    return codes.get(provider, f"*123*1*{amount}#")

def get_exchange_rate(crypto_type):
    """Récupère le taux de change (simulation)"""
    # En production, utiliser une API comme CoinGecko
    rates = {
        'bitcoin': 45000.00,
        'ethereum': 3000.00,
        'litecoin': 150.00,
        'usdt': 1.00,
        'usdc': 1.00,
    }
    
    return rates.get(crypto_type, 1.00)
