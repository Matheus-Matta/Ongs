import re

class ValidationError(Exception):
    """
    Exceção personalizada para validação de dados.
    """
    def __init__(self, errors):
        self.errors = errors
        super().__init__("Validation error occurred.")

def validate_user_data(data):
    """
    Valida os dados do usuário.
    :param data: dict contendo os dados do usuário
    :raises ValidationError: se houver erros de validação
    :return: dict com dados formatados se válido
    """
    errors = {}

    # Validação do número de telefone
    
