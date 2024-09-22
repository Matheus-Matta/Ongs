from account.data import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User

# carregar pagina de login
def account_login(request):
    return render(request,'auth/login.html')

# authenticcar user para login
def account_auth(request):
    try:
        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('password')
            user = User.objects.get(email=email, password=password)
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
            else:
                messages.error(request, 'Credenciais inválidas. Tente novamente.')

        return redirect('index')
    except Exception as e:
        messages.error(request, f'Error ao logar {str(e)}')
        return redirect('account_login')

# deslogar user
def account_logout(request):
    return