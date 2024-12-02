from django.contrib import admin
from django.urls import path , include

from account.views.user.views import ( 
    account_block,
    account_delete,
    account_edit,
    follow_user,
    get_profile,
    get_followers,
    get_organizations
) 

from account.views.access.views import ( 
    account_login,
    account_logout,
    account_auth,
    account_register,
    
) 

from account.views.post.views import ( 
    create_post,
    load_posts,
    participar_evento,
    event_list,
    delete_event,
    add_comment,
    load_comments,
    add_like,
)
from account.views.chat.views import ( 
   chat_list,
)

urlpatterns = [
    
    # base url account 'base_url/account/'
    
    # views para controle de acesso 
    path('login', account_login, name='account_login'), # 'base_url/account/login'
    path('logout', account_logout, name='account_logout'), # 'base_url/account/logout'
    path('auth', account_auth, name='account_auth'), # 'base_url/account/auth'
    path('register', account_register, name='account_register'), # 'base_url/account/register'
    
    
    # views para controle de usuario
    path('edit', account_edit, name='account_edit'), # 'base_url/account/edit'
    path('block', account_block, name='account_block'), # 'base_url/account/block'
    path('delete', account_delete, name='account_delete'), # 'base_url/account/delete'
    path("follow/<int:user_id>/", follow_user, name="follow_user"),
    path("get-profile/<int:user_id>/", get_profile, name="get_profile"),
    path("get-followers", get_followers, name="get_followers"),
    path("get_organizations/<int:page>/", get_organizations, name="get_organizations"),
     
     
     
    # views para controle de post
    path('create_post', create_post, name='create_post'),
    path("load-posts/<int:page>/<int:postId>/", load_posts, name="load_posts"),
    path("participar_evento/<int:event_id>/", participar_evento, name="participar_evento"),
    path("add_comment/<int:post_id>/", add_comment, name="add_comment"),
    path('load-comments/<int:post_id>/<int:page>/', load_comments, name='load_comments'),
    path('posts/add_like/<int:post_id>/', add_like, name='add_like'),
    
    
    # views para controle de eventos
    path("events/", event_list, name="events"),
    path('events/delete/<int:event_id>/', delete_event, name='delete_event'),
    
    # views para controle do chat
    path("chat", chat_list, name="chat"),
]
