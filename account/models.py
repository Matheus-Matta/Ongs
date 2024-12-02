from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import random
import os
import shutil
from django.utils.timezone import now


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

def user_profile_image_path(instance, filename):
    """
    Define o caminho dinâmico para armazenar a imagem de perfil do usuário.
    O formato será: account/{instance.id}/profile/{instance.id}-profile{extension}.
    """
    extension = os.path.splitext(filename)[1]  # Obtém a extensão do arquivo
    return f"account/{instance.id}/profile/{instance.id}-profile{extension}"


class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ("volunteer", "Voluntário"),
        ("organization", "Organização"),
    ]
    typeuser = models.CharField(max_length=15, choices=USER_TYPE_CHOICES, default="volunteer")
    email = models.EmailField(unique=True)  # Garante que o email seja único
    following = models.ManyToManyField("self", symmetrical=False, related_name="followers", blank=True)
    is_blocked = models.BooleanField(default=False)
    categories = models.ManyToManyField("Category", related_name="users", blank=True)
    profile_image = models.ImageField(
        upload_to=user_profile_image_path,  # Define o diretório dinâmico para a imagem
        blank=True,
        null=True
    )
    
    phone_number = models.CharField(
        max_length=15,  # Suporta formatos internacionais, ex: +55 21 91234-5678
        blank=True,
        null=True,
        default="",
    )
    
    bio = models.TextField(
        max_length=500,  # Limita a bio a 500 caracteres
        blank=True,
        null=True,
        default="",
        
    )

    def save(self, *args, **kwargs):
        creating = not self.pk  # Verifica se o usuário está sendo criado
        super().save(*args, **kwargs)  # Salva o objeto para garantir que o ID exista

        # Se a imagem de perfil não foi definida, copie uma imagem padrão
        if not self.profile_image and creating:
            random_number = random.randint(1, 6)
            static_image_path = os.path.join(settings.BASE_DIR, 'static', f'images/users/user-{random_number}.png')
            media_image_dir = os.path.join(settings.MEDIA_ROOT, f"account/{self.id}/profile/")
            media_image_path = os.path.join(media_image_dir, f"{self.id}-profile.png")
            
            # Certifica-se de que o diretório no MEDIA_ROOT existe
            os.makedirs(media_image_dir, exist_ok=True)

            # Clona a imagem padrão para o diretório de mídia
            if os.path.exists(static_image_path):
                shutil.copy(static_image_path, media_image_path)
                # Atualiza o campo profile_image com o caminho do arquivo copiado
                self.profile_image = f"account/{self.id}/profile/{self.id}-profile.png"
                super().save(update_fields=["profile_image"])  # Atualiza apenas o campo profile_image
            else:
                raise FileNotFoundError(f"Imagem padrão {static_image_path} não encontrada.")

    def followers_count(self):
        return self.following.count()

    def __str__(self):
        return self.username

class Address(models.Model):
    STATE_CHOICES = [
        ("AC", "Acre"),
        ("AL", "Alagoas"),
        ("AP", "Amapá"),
        ("AM", "Amazonas"),
        ("BA", "Bahia"),
        ("CE", "Ceará"),
        ("DF", "Distrito Federal"),
        ("ES", "Espírito Santo"),
        ("GO", "Goiás"),
        ("MA", "Maranhão"),
        ("MT", "Mato Grosso"),
        ("MS", "Mato Grosso do Sul"),
        ("MG", "Minas Gerais"),
        ("PA", "Pará"),
        ("PB", "Paraíba"),
        ("PR", "Paraná"),
        ("PE", "Pernambuco"),
        ("PI", "Piauí"),
        ("RJ", "Rio de Janeiro"),
        ("RN", "Rio Grande do Norte"),
        ("RS", "Rio Grande do Sul"),
        ("RO", "Rondônia"),
        ("RR", "Roraima"),
        ("SC", "Santa Catarina"),
        ("SP", "São Paulo"),
        ("SE", "Sergipe"),
        ("TO", "Tocantins"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="address")  # Relaciona com o usuário
    city = models.CharField(max_length=100, default="Não informado")
    state = models.CharField(max_length=2, choices=STATE_CHOICES, default="Não informado")  # Limita os valores aos estados
    postal_code = models.CharField(max_length=8, default="Não informado")  # Formato '12345678'
    address_line = models.CharField(max_length=255, default="Não informado")  # Rua, Avenida, etc.
    address_number = models.CharField(max_length=10, default="Não informado")  # Número do endereço

    def __str__(self):
        # Se algum campo não estiver preenchido, retorna "Não informado"
        return (
            f"{self.address_line or 'Não informado'}, "
            f"{self.address_number or 'Não informado'} - "
            f"{self.city or 'Não informado'}/{self.state or 'Não informado'}"
        )
        
        


def post_image_upload_path(instance, filename):
    """
    Define o caminho dinâmico para armazenar imagens do post.
    O nome do arquivo será uma combinação do timestamp e do nome original.
    """
    timestamp = now().strftime("%Y%m%d%H%M%S")  # Timestamp único com precisão de segundos
    unique_filename = f"{timestamp}_{filename}"  # Combina o timestamp com o nome original
    return f"account/{instance.user.id}/posts/{unique_filename}"

class Event(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="events")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date = models.DateField()
    time = models.TimeField()

    def __str__(self):
        return f"Event '{self.title}' by {self.user.username} on {self.date} at {self.time}"
    
class Volunteer(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="volunteers")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="volunteering_events")
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Volunteer {self.user.username} for Event {self.event.title}"
    
class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, related_name="posts", null=True, blank=True)
    text = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="liked_posts", blank=True)   
    
    def like_count(self):
        return self.likes.count()

    def comment_count(self):
        return self.comments.count()
     
    def __str__(self):
        return f"Post by {self.user.username} at {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
    
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    mentioned_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="mentioned_in_comments", blank=True)  # Relacionamento para usuários mencionados
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post}"

class ImagePost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=post_image_upload_path)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="image_posts"
    )

    def __str__(self):
        return f"Image for Post ID {self.post.id}"