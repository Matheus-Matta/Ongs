from account.data import *
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from account.models import User
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