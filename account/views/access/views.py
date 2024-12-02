from account.data import *
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from account.models import User, Category, Address
from django.db import transaction
from django.http import JsonResponse
import re
# carregar pagina de login
def account_login(request):
    return render(request,'auth/login.html')

# authenticcar user para login
def account_auth(request):
    try:
        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('password')

            user = authenticate(request, email=email, password=password)
            
            if user:
                    login(request, user)
                    return redirect('index')
            else:
                messages.error(request, 'Usuário não encontrado.')
        return redirect('account_login')
    except Exception as e:
        messages.error(request, f'Erro ao logar: {str(e)}')
        return redirect('account_login')

# deslogar user
def account_logout(request):
    logout(request)
    return redirect('account_login')

def account_register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        phone_number = request.POST.get("phone_number")
        address_line = request.POST.get("address_line")
        address_number = request.POST.get("address_number")
        postal_code = request.POST.get("postal_code")
        bio = request.POST.get("bio")
        typeuser = request.POST.get("typeuser")
        categories = request.POST.getlist("categories[]")
        state = request.POST.getlist("state")
        city = request.POST.getlist("city")
        

        # Verificar se o email já está registrado
        if User.objects.filter(email=email).exists():
            return JsonResponse(
                {"success": False, "field": "email", "message": "Este email já está cadastrado."}, 
                status=400
            )
            
         # Verificar se o email já está registrado
        if User.objects.filter(username=username).exists():
            return JsonResponse(
                {"success": False, "field": "username", "message": "Este Username já está cadastrado."}, 
                status=400
            )

        # Validar a senha
        if not re.search(r'[A-Z]', password) or not re.search(r'[0-9]', password) or not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return JsonResponse(
                    {"success": False, "field": "password", "message": "A senha deve conter pelo menos uma letra maiúscula um caractere especial e um número."},
                    status=400
                )

        # Verifica se as senhas coincidem
        if password != confirm_password:
            return JsonResponse(
                {"success": False, "field": "confirm_password", "message": "As senhas não coincidem."},
                status=400
            )

        # Registra o usuário e associa as categorias e endereço
        try:
            with transaction.atomic():
                # Criar o usuário
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    typeuser=typeuser,
                    phone_number=phone_number,
                    bio=bio,
                )

                if categories:
                    selected_categories = Category.objects.filter(id__in=categories)
                    user.categories.set(selected_categories)  # Atualiza as categorias associadas

                # Criar o endereço do usuário
                Address.objects.create(
                    user=user,
                    address_line=address_line,
                    address_number=address_number,
                    postal_code=postal_code,
                    state=state[0] if state else None,
                    city=city[0] if city else None,
                )
                
            user = authenticate(request, email=email, password=password)
            if user:
                 login(request, user)
            return JsonResponse({"success": True, "message": "Usuário registrado com sucesso!"})

        except Exception as e:
            return JsonResponse({"success": False, "message": f"Erro ao registrar usuário: {str(e)}"}, status=500)

    # Passa as categorias para o template
    categories = Category.objects.all()
    return render(request, "auth/register.html", {"categories": categories})
