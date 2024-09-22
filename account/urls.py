from django.contrib import admin
from django.urls import path , include

from account.views.user.views import ( 
    account_block,
    account_delete,
    account_edit
) 
from account.views.access.views import ( 
    account_login,
    account_logout,
    account_auth
) 

urlpatterns = [
    
    # base url account 'base_url/account/'
    
    # views para controle de acesso 
    path('login', account_login, name='account_login'), # 'base_url/account/login'
    path('logout', account_logout, name='account_logout'), # 'base_url/account/logout'
    path('auth', account_auth, name='account_auth'), # 'base_url/account/auth'
    
    # views para controle de usuario
    path('edit', account_edit, name='account_edit'), # 'base_url/account/edit'
    path('block', account_block, name='account_block'), # 'base_url/account/block'
    path('delete', account_delete, name='account_delete'), # 'base_url/account/delete'
    
    
]
