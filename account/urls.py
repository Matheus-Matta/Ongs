from django.contrib import admin
from django.urls import path , include

from account.views.user.views import ( 
    account_block,
    account_delete,
    account_edit,
    follow_user,
    get_profile
) 

from account.views.access.views import ( 
    account_login,
    account_logout,
    account_auth,
) 

from account.views.post.views import ( 
    create_post,
    load_posts,
    participar_evento,
    event_list,
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
    path("follow/<int:user_id>/", follow_user, name="follow_user"),
    path("get-profile/<int:user_id>/", get_profile, name="get_profile"),
    
    
    path('create_post', create_post, name='create_post'),
    path("load-posts/<int:page>/", load_posts, name="load_posts"),
    path("participar_evento/<int:event_id>/", participar_evento, name="participar_evento"),
    
    
    path("events/", event_list, name="event_list"),
]
