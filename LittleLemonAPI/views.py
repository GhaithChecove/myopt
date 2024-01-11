from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from rest_framework import status
from rest_framework.decorators import api_view 
# Create your views here.
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated , IsAdminUser
from . import serializers as sir
from . import models as m
from django.contrib.auth.models import User ,Group
import json
from decimal import Decimal
from django.http import HttpResponse

@api_view(['GET','POST','PUT'])
@permission_classes([IsAuthenticated])
def menu_items(request):
    items =sir.Menu_item_serializer()
    '''here to list all the menu items for all users '''
    print('in function')
    if request.method =="GET":
        print('in if')
        items =m.MenuItem.objects.select_related().all()
        print(items)
        to_order = request.query_params.get("ordering")
        to_search = request.query_params.get("search")
        category = request.query_params.get("category")
        to_price = request.query_params.get("price")
        perpage = request.query_params.get("perpage" , default =2)
        page = request.query_params.get('page' ,default=1)
        if to_order:
            ordering_fields = to_order.split(",")
            items = items.order_by(*ordering_fields)
        if to_search:
            items = items.filter(title__contains=to_search)
        if category:
            items = items.filter(category__title=category)
        if to_price:
            items = items.filter(price = to_price)
        ## pagination section 
        paginator =  Paginator(items , per_page=perpage)
        try:
            items=paginator.page(number=page)
        except EmptyPage:
            items=[]

        print(items)
        items = sir.Menu_item_serializer(items, many=True)
    
    if request.method=="POST":
        if request.user.groups.filter(name='Manager').exists():
            serialized_item = sir.Menu_item_serializer(data=request.data)
            serialized_item.is_valid(raise_exception=True)
            serialized_item.save()

            return Response(serialized_item.validated_data  , status.HTTP_201_CREATED)
        else:
            items={'message':"Only Manager can add new MenuItem"}
            return Response(items,status.HTTP_403_FORBIDDEN)

    
    return Response(items.data)

@api_view(['GET' , 'PUT' , 'PATCH' , 'DELETE'])
@permission_classes([IsAuthenticated])
def single_menuitems(request , menuitem):
    print("this is Menu item id " ,type(menuitem))
    items = sir.Menu_item_serializer()
    if request.method == "GET":
        items = m.MenuItem.objects.select_related().get(id=menuitem)
        items = sir.Menu_item_serializer(items)
        
    elif request.method=="PUT" or request.method=="PATCH":
        if request.user.groups.filter(name="Manager").exists():
            print(request.user.username)
            items = m.MenuItem.objects.select_related().get(id=request.POST['menuitem'])
            print(items)
            ser_data = sir.Menu_item_serializer( items, data=request.data)
            ser_data.is_valid(raise_exception=True)    
            ser_data.save()
            return Response(ser_data.data , status.HTTP_201_CREATED)
        else:
            return Response({"message":"This post request is invalid only managers can do it"} , status.HTTP_403_FORBIDDEN)   
        
        
        return Response(items.data, status.HTTP_200_OK)

    
    if request.method == "DELETE":
        if request.user.groups.filter(name = "Manager").exists():
            item =m.MenuItem.objects.select_related().get(id=menuitem)
            item.delete()
            return Response({"message":"The item {0} has been delete ".format(item.title )} , status=status.HTTP_200_OK)
        else: 
            return Response({"message":"This Operation just done by the managers"} , status.HTTP_403_FORBIDDEN)
        
        
    return Response(items.data )



@api_view()
@permission_classes([IsAdminUser])
def add_menu_itme(request):
    if request.method=='GET':
        menu_items  =m.MenuItem.objects.all()
        menu_items = sir.Menu_item_serializer(menu_items)

        return Response({'menuItems':menu_items} ,status.HTTP_200_OK)

    elif request.method=='POST':
        try:
            menu_item = request.data
            menu_item = sir.Menu_item_serializer(menu_item)
            if menu_item.is_valid():
                menu_item.save()
                return Response({'message':"Menu Item was added successfully"})
            else:
                message= 'Please enter a valid Menu item'
                return Response({'message':message})
        except Exception:
            return Response({'message': 'Exception occured'})
    elif request.method =='DELETE':
        try: 
            menu_item = request.POST['menuitem']
            menu_item = m.MenuItem.objects.get(title=menu_item)
            if menu_item:
                menu_item.delete()
                return Response({'message':'Menu Item was deleted successfully'})
            else:
                return Response({'message':'No Menu Item match entered value'})
        except Exception:
            return Response({'message':'Exception was raised'})


@api_view()
@permission_classes([IsAdminUser])
def admin_category_management(request):
    if request.method=="GET":
        
        categories = m.Category.objects.all()
        categories = sir.Category_serializer(categories)

        return Response({'message':categories.data})
    elif request.method=='POST':
        category = request.data
        category = sir.Category_serializer(category)
        if category.is_valid():
            category.save()
            return Response({'message':category.data})
        else:
            return Response({'message':'You should enter a valid category'})





@api_view(['GET','POST'])
@permission_classes([IsAdminUser])
def manager(request):
    if request.method=="POST":
        username = request.data['username']
        if username:
            user = get_object_or_404(User , username=username)
            managers=Group.objects.get(name='Manager')
            if request.method=='POST':
                user.groups.add(managers)
                
            return Response({"message":"ok"},status.HTTP_200_OK)
    elif request.method=="GET":
        print('get method to list all mangers')
        managers = m.User.objects.filter(groups__name = "Manager")
        managers = sir.Users_serlializer(managers , many=True)

        return Response({'managers':managers.data} , status=status.HTTP_200_OK)

            
    return Response({"message":"error"} , status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_manager_user(request , userId):
    user= get_object_or_404(User , id= userId)
    if userId:
        if user.groups.filter(name='Manager').exists():
            manager =Group.objects.get(name='Manager')
            user.groups.remove(manager)
        else:
            return Response({"message":"User does not exist in Manager group"})
    return Response({'message':'the user {0} has been deleted successfully .'.format(user.username)} , status=status.HTTP_200_OK)



@api_view(['GET','POST'])
def post_delivery_user(request):
    if request.user.groups.filter(name="Manager").exists():
        username = request.data['username']
        if request.method=='POST':    
            if username:
                user = get_object_or_404(User , username=username)
                delivery=Group.objects.get(name='Delivery Crew')
                user.groups.add(delivery)
                return Response({"message":"User added successfully to the Delivery Group"} , status.HTTP_200_OK)
        if request.method=="GET":
            
            delivery =User.objects.all()
            # print('this is the list of users ' , delivery)
            delivery_list = delivery.filter(groups__name = "Delivery Crew").values_list()
            # delivery = User.objects.filter(username = delivery.username)
            # delivery = list(delivery)
            # print("this is a list of delivery users  " ,delivery_list)
            # print(type(delivery_list)) 
            # delivery_list = sir.Users_serlializer(delivery_list)
            return Response(delivery_list ,status=status.HTTP_200_OK)

    else:
        return Response({"message":"only mangers can see Delivery Crew"} , status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_delivery_user(request , userId):
    user= get_object_or_404(User , id= userId)
    print(user.username)
    if userId:
        if request.user.groups.filter(name='Manager').exists():
            delivery_crew =Group.objects.get(name='Delivery Crew')
            user.groups.remove(delivery_crew)
        else:
            return Response({"message":"User does not exist in Manager group"})
    return Response({'message':'the user {0} was been deleted successfully .'.format(user.username)} , status=status.HTTP_200_OK)


@api_view(['GET','POST','DELETE'])
@permission_classes([IsAuthenticated])
def cart_menu_item(request):
    message = ''
    if request.method=="POST":
        manger = request.user.groups.filter(name="Manager").exists()
        delivery = request.user.groups.filter(name="Delivery Crew").exists()
        if manger or delivery:
            
            return Response({"message":"this operation only for customers"}) 
        else:
            
            cart_post = request.POST
            print('this is cart post data ' , cart_post)
            cart_user = request.user
            cart = m.Cart.objects.filter(user=cart_user)
            
            try:
                cart_item = cart_post['menuitem']
                
                print("this is a menu item name" , cart_item)
                cart_item =m.MenuItem.objects.get(title=cart_item)
                cart_quantity =  cart_post['quantity']
                cart_unit_price = cart_item.price
                items_total_price = Decimal(cart_unit_price)*Decimal(cart_quantity)
                print("this is the cart content" , cart_user , cart_item , cart_quantity  , cart_unit_price )
                
                
                cart_object= m.Cart(user = cart_user , menuitem=cart_item , quantity=cart_quantity ,unit_price = cart_unit_price,price= items_total_price )
                
                
                print("this is a cart object created with initial values from post request" , cart_object)
                # cart_ser = sir.Cart_serializer(data=cart_object)
                print("this is serialized cart object " ,  cart_object)
                cart_object.clean()
                cart_object.save()
                return Response({"message":"item added to the cart successfully"})
            except Exception:
                # raise Exception('DoesNotExist')
                print("exeption raised")
                return Response({'message':'Menu Item value Error DoesNotException raised '},status.HTTP_404_NOT_FOUND)
            
    elif request.method=="GET":
        user = request.user
        user_cart = m.Cart.objects.filter(user =user)
        print("user_cart" , user_cart)
        if user_cart:
            cart_ser = sir.Cart_serializer(user_cart ,many=True) 
            
            return Response(cart_ser.data , status.HTTP_200_OK)
        else:
            return Response ({'message':'The cart is empy and Nothing to show'})
    elif request.method=="DELETE":
        user = request.user
        cart = m.Cart.objects.filter(user = user)
        if cart:
            cart.delete()
        else:
            message = 'This cart does not exists'
            return Response({'message':message})

        return Response({'message':'All the cart menu items was deleted succefully'} , status.HTTP_200_OK)



def create_order_items(user,user_cart):
    '''this is a method to create order items'''
    new_order = []
    total =Decimal()
    order_user = ''
     
     
    for item in user_cart:
        
        order_user = item.user
        menuitem = item.menuitem
        quantity = item.quantity
        unit_price = item.unit_price
        price = item.price
        new_order_item =m.OrderItem( order=order_user ,menuitem=menuitem , quantity=quantity , unit_price=unit_price,price =price)
        total += item.price
        new_order_item.clean()
        new_order_item.save()
    
    return order_user , total
    
    
    
# def updateOrderItem(user , user_cart):
#     orderItem = m.OrderItem.objects.all()
#     new_order_item = m.OrderItem()
#     user_cart_items=user_cart
#     for i in user_cart_items:
#         for j in orderItem:
#             if i.menuitem ==j.menuitem:
#                 i.quanity+=j.quantity
                
#     user_cart_items.clean()
#     user_cart_items.save()
    
#     return user_cart_items
                
             
    


@api_view(['GET','POST','DELETE'])
@permission_classes([IsAuthenticated])
def order_management(request):
    user = request.user
    print('the user object which make the request is ' , user)
    if request.user.groups.filter(name="Manager").exists():
        orders = m.Order.objects.all()   
        print('orders ' , orders.values_list())
        orders = sir.Order_serializer(orders , many = True) 
        order_items = m.OrderItem.objects.all()
        order_items = sir.Order_item_serializer(order_items,many=True)
        
        return Response({'orders':orders.data , 'order_items':order_items.data})
    elif user:
        if request.method=='GET':
            if user.groups.filter(name='Delivery Crew').exists():
                # this will get all the orders of delivery crew user
                orders = m.Order.objects.filter(delivery_crew =user)
                orders = sir.Order_serializer(orders , many=True)
                return Response({'orders':orders.data} ,status = status.HTTP_200_OK)
            else:
                new_order = m.Order.objects.filter(user=user)
                print(new_order)
                order = sir.Order_serializer(new_order,many=True)
                
                return Response(order.data,status=status.HTTP_200_OK) 
       
        elif request.method=='POST':
            
            check = m.Cart.objects.filter(user =user)
            print("check",check)
            if check:
                
                user_cart = m.Cart.objects.filter(user=user)
                try:
                    order_user , total =create_order_items(user,user_cart=user_cart)
                except:
                   return Response({'message':'Exception was raised this you can\'t add two menu items for your cart '})
                newOrder = m.Order(user =user  ,total = total)
                newOrder.clean()
                newOrder.save()
                check.delete()
                return Response({'message':'The order of customer name = {} and The Order created successfully'.format(user.first_name)} ,status=status.HTTP_201_CREATED) 
            
                    
            else:
                return Response({'message':'This user has not any Cart to Order'})
        
        
        
@api_view(['GET','POST','DELETE' , 'PUT' , 'PATCH'])
@permission_classes([IsAuthenticated])
def single_order(request,orderId):
    if request.method=="GET":    
        if orderId:
            # try:
                # orders = m.Order.objects.filter(user=request.user.id)
            user = request.user
            singleOrder = m.Order.objects.filter( user=user )
            singleOrder =  singleOrder.filter(id=orderId)
            single_order_items = m.OrderItem.objects.filter( order=user)
            # single_order_items = single_order_items.filter(id=orderId)
            
            print('single order' , singleOrder , ' single order itmes ' , single_order_items)
            if singleOrder and single_order_items:
                order = sir.Order_serializer(singleOrder , many=True)
                order_items = sir.Order_item_serializer(single_order_items , many = True)

                return Response({'order':order.data  , 'orderItems':order_items.data})
            else:
                return Response({'message':'this user has not any Order'})
    
    elif request.method =="PUT" or request.method=="PATCH":
        print('Get in the PUT and PATCH Methods')
        manager_user = request.user.groups.filter(name='Manager').exists()
        delivery_user = request.user.groups.filter(name='Delivery Crew').exists()
        
        print("delivery crew user " , delivery_user)
        if delivery_user:
            delivery_user=m.User.objects.get(username=request.user.username)
            print('get delivery user name' , delivery_user)
        order_client =m.User()   
        if manager_user or delivery_user:
            print('get in the if manager check')
            order_delivery = request.query_params.get('delivery')
            print("query params order_delivery " , order_delivery)
            order_client = request.POST['username']
            print("order_client " , order_client)

            
            
            check_delivery = m.User.objects.get(username = order_delivery)
            
            print("check_delivery = m.User.objects.get(username = order_delivery) " , check_delivery)
            
            check_delivery_user = check_delivery.groups.filter(name="Delivery Crew").exists()
            print("check delivery user " , check_delivery)
            
            if check_delivery_user and order_client:
                print('ger in the update body if ')
                # get the client of target order to update its order
                client = m.User.objects.get(username=order_client)
                print('client >>>> ', client)
                # get the order ot targeted user
                order = m.Order.objects.filter(user=client)
                
                # get the order with corresponding orderId
                order = order.get(id=orderId)
                print('order ,,,,, ' , order)
                order_status = request.query_params.get('status')
                print("order delivery ghaith")
                if order_delivery:
                    delivery = m.User.objects.get(username = order_delivery)

                    order.delivery_crew =delivery
                    
                    order.save()
                    print("save done")
                    
                    
                if order_status:
                    print('order status ' , order_status)
                    if order_status =='0' or order_status=='1':
                        print('order status in if loop' , order_status)
                        order.status = order_status
                        order.save()
                    else:
                        return Response({'message':'the entered status is not valid'})
                else:
                    return Response({'message':'no thing to update'})
            return Response({'message':'the The order delivery {} was added to the order number {} for client '.format(order_delivery ,order_client, request.user  )})
        else:
            return Response({'message':'this type of requests allowed only for the Managers'})       
                
                
    elif request.method=='DELETE':
        if request.user.groups.filter(name='Manager').exists():
            # get the requested user that we want delete its order from the request.GET method
            target_user = request.POST['user']
            # get the user object which correspond the the requested user
            order_user = m.User.objects.get(username=target_user)
            # this will get all orders with considerd orderId and user id
            # order_data = m.Order.objects.filter(id=orderId)
            # order_data = order_data.filter(order_user)
            
            try :
                check_order = m.Order.objects.filter(user = order_user)
                check_order_items = m.OrderItem.objects.filter(order  =order_user)

                if check_order and check_order_items:
                    check_order_items.delete()
                    check_order.delete()
                    return Response({'message':'The Order and Order items was deleted successfully '} , status=status.HTTP_200_OK)
                
                else:
                    return Response({'message':'This User orders is empty'})
                
            except Exception:
                # raise Exception
                return Response({'message':'This user orders is empty and raised an Exception'} , status=status.HTTP_404_NOT_FOUND)
        else:
            # The Delete operation allowed only for managers
            return Response({'message':'Delete operation allowed only for Managers'})
            
    else:
        return Response({'message':'there is no compatible type of request method'})  
            
        # except Exception:
        #     raise Exception
    
    