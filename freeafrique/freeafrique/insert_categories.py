from main.models import Category

categories = [
    ("Développement Web", "Projets web"),
    ("Design", "Projets de design"),
    ("Marketing Digital", "Projets marketing"),
    ("Rédaction", "Projets de rédaction"),
    ("Traduction", "Projets de traduction"),
    ("Graphisme", "Projets graphiques"),
    ("Vidéo", "Projets vidéo"),
    ("Audio", "Projets audio"),
]

for name, desc in categories:
    Category.objects.get_or_create(name=name, defaults={"description": desc})

print("Catégories ajoutées !")