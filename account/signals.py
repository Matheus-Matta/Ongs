from django.conf import settings
from django.db.models.signals import post_migrate
from account.models import User, Address, Category
import environ
import requests

# Inicializar o django-environ
env = environ.Env()
environ.Env.read_env(settings.BASE_DIR / ".env")  # Certifique-se de que settings.BASE_DIR está definido no settings.py


def get_server_location():
    """
    Função para obter a localização aproximada do servidor baseado no IP.
    """
    try:
        response = requests.get("https://ipinfo.io/json")
        if response.status_code == 200:
            data = response.json()
            city = data.get("city", "Unknown")
            region = data.get("region", "Unknown")
            postal = data.get("postal", "00000")
            return city, region, postal
    except requests.RequestException:
        pass
    return "Unknown", "Unknown", "00000"


def create_default_user(sender, **kwargs):
    """
    Signal para criar um usuário padrão usando as variáveis de ambiente.
    """
    username = env("DEFAULT_USER_USERNAME", default="admin")
    email = env("DEFAULT_USER_EMAIL", default="admin@admin.com")
    password = env("DEFAULT_USER_PASSWORD", default="admin")

    if not User.objects.filter(username=username).exists():
        user = User.objects.create_superuser(username=username, email=email, password=password)
        print(f"Usuário padrão criado: {username}")

        # Criar endereço padrão
        city, state, postal_code = get_server_location()
        Address.objects.create(
            user=user,
            city=city,
            state=state,
            postal_code=postal_code
        )
        print(f"Endereço padrão criado para o usuário {username}: {city}, {state}, {postal_code}")
        
def create_default_category(sender, **kwargs):
    """
    Signal para criar categorias.
    """
    CATEGORIES = [
        "Ajuda a cães",
        "Ajuda a gatos",
        "Resgate de animais",
        "Proteção ambiental",
        "Educação infantil",
        "Assistência a idosos",
        "Apoio a pessoas com deficiência",
        "Ajuda a refugiados",
        "Combate à fome",
        "Habitação popular",
        "Saúde pública",
        "Apoio psicológico",
        "Apoio a vítimas de violência doméstica",
        "Inclusão digital",
        "Reabilitação de dependentes químicos",
        "Empoderamento feminino",
        "Direitos humanos",
        "Educação para jovens",
        "Cultura e artes",
        "Apoio a comunidades indígenas",
    ]
    
    for category in CATEGORIES:
        if not Category.objects.filter(name=category).exists():
            Category.objects.get_or_create(name=category)
            print(f"Categoria {category} Criadas!!")
            

# Conectar o signal ao post_migrate
post_migrate.connect(create_default_user)
post_migrate.connect(create_default_category)



