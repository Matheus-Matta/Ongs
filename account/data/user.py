from django.shortcuts import get_object_or_404
from account.models import User
from django.core.exceptions import ValidationError

class UserService:
    
    @staticmethod
    def get_user(user_id):
        """Pega um usuário pelo ID."""
        try:
            return get_object_or_404(User, id=user_id)
        except ValueError as e:
            raise ValueError(f"Error Value: {e}")

    @staticmethod
    def create_user(**fields):
        """Cria um novo usuário."""
        try:
            user = User(**fields)  # Use o unpacking para passar os campos
            user.set_password(fields.get('password'))  # Para criptografar a senha
            user.full_clean()  # Valida os dados do usuário
            user.save()
            return user
        except ValueError as e:
            raise ValueError(f"[account] Error Value: {e}")
        except ValidationError as e:
            raise ValueError(f"[account] Error Value: {e}")

    @staticmethod
    def update_user(**fields):
        """Atualiza os dados de um usuário."""
        try:
            user = UserService.get_user(fields.get('user_id'))
            if isinstance(user, str):  # Se retornou uma mensagem de erro
                raise ValueError(user)  # Levanta um ValueError com a mensagem
            for key, value in fields.items():
                setattr(user, key, value)
            user.full_clean()  # Valida os dados antes de salvar
            user.save()
            return user
        except ValueError as e:
            raise ValueError(f"[account] Error Value: {e}")
        except ValidationError as e:
            raise ValueError(f"[account] Error Value: {e}")

    @staticmethod
    def delete_user(user_id):
        """Deleta um usuário."""
        try:
            user = UserService.get_user(user_id)
            if isinstance(user, str):  # Se retornou uma mensagem de erro
                raise ValueError(user)  # Levanta um ValueError com a mensagem
            user.is_active = False
            user.save()
        except ValueError as e:
            raise ValueError(f"[account] Error Value: {e}")

    @staticmethod
    def block_user(user_id):
        """Bloqueia um usuário."""
        try:
            user = UserService.get_user(user_id)
            if isinstance(user, str):  # Se retornou uma mensagem de erro
                raise ValueError(user)  # Levanta um ValueError com a mensagem
            user.is_blocked = True
            user.save()
            return user
        except ValueError as e:
            raise ValueError(f"[account] Error Value: {e}")
