from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# página principal famosa feed page
@login_required
def index(request):
    user = request.user  # Obtém o usuário autenticado
    return render(request, 'apps/social/feed.html', {'user': user})