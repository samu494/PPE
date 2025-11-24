import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freeafrique.settings')
django.setup()

from django.contrib.auth.models import User
from main.models import Message, Client, Freelancer

SAMPLE_MESSAGES = [
    "Bonjour, je suis intéressé par votre projet.",
    "Merci pour votre message ! Pouvez-vous préciser le délai ?",
    "Je peux livrer en 5 jours avec des révisions incluses.",
    "Parfait, quel serait le budget estimé ?",
    "Je propose 300€, incluant tests et documentation.",
    "D'accord, lançons la collaboration.",
]

def create_sample_conversations(num_conversations: int = 5):
    clients = list(Client.objects.select_related('user'))
    freelancers = list(Freelancer.objects.select_related('user'))
    if not clients or not freelancers:
        print("Pas assez d'utilisateurs pour créer des conversations.")
        return
    created = 0
    for _ in range(num_conversations):
        client = random.choice(clients).user
        freelancer = random.choice(freelancers).user
        if client.id == freelancer.id:
            continue
        # Check if conversation exists
        exists = Message.objects.filter(sender=client, receiver=freelancer).exists() or \
                 Message.objects.filter(sender=freelancer, receiver=client).exists()
        if exists:
            continue
        # Create 4-6 messages alternating
        turn_users = [client, freelancer]
        for i in range(random.randint(4, 6)):
            sender = turn_users[i % 2]
            receiver = turn_users[(i + 1) % 2]
            content = random.choice(SAMPLE_MESSAGES)
            Message.objects.create(sender=sender, receiver=receiver, content=content)
        created += 1
    print(f"Conversations créées: {created}")

if __name__ == '__main__':
    create_sample_conversations()