from django.urls import path
from . import views as v

from rest_framework.authtoken.views import ObtainAuthToken

urlpatterns = [
    ## my website end-points
    ########## MENU-Items endpoints
    ## this is used for (GET  , POST , PUT , PATCH , DELETE)
    path('menu-items' ,v.menu_items ,  name='menu_items' ),
    ## this is for Using all http methods with single item
    path('menu-items/<int:menuitem>' ,  v.single_menuitems , name = 'menu_item'),
    # ########## User Group management endpoints 
    # ## GET and POST methods to deal with users by managers
    path('groups/manger/users' , v.manager , name='manager'),
    
    # ## Working with one single user 
    path ('groups/manager/users/<int:userId>' ,  v.delete_manager_user , name = 'users'),

    # ## costummizing the delivery crew 
    path ('groups/delivery-crew/users' , v.post_delivery_user , name = 'crew_users'),
    path('groups/delivery-crew/users/<int:userId>' , v.delete_delivery_user , name ='crew'),

    # ######## Cart management endpoints 
    # ## get and post delete menu items with cart based on current user token
    path('cart/menu-items', v.cart_menu_item , name='menu_item'),

    # ######## order management endpoints 
    path('orders' ,v.order_management , name ='orders'),
    # ## this will make all http methods on a single order based on user token
    path('orders/<int:orderId>' , v.single_order , name='order'),
    # path('secret/' , v.secret , name="secret"),
    path('api-token-auth/' , ObtainAuthToken.as_view()),
    
    ## this is functionalities which admin can does
    path('admin/menuitem' , v.add_menu_itme , name='add_menu_item'),
    path('admin/category' , v.add_menu_itme , name='add_menu_item'),
    
]
