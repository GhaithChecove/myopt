from rest_framework import serializers
from . import models as m 
from decimal import Decimal


class Category_serializer(serializers.ModelSerializer):

    class Meta:
        model=m.Category
        fields = ['id','slug', 'title']

class Menu_item_serializer(serializers.ModelSerializer):
    category = Category_serializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = m.MenuItem
        fields = ['id','title'  ,'category' , 'category_id' , 'price', 'featured']
        
class Cart_serializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField( method_name="price_of_total"  )
    price = serializers.DecimalField(decimal_places=2,max_digits=6 )
    class Meta:
        model= m.Cart
        fields = ['id', 'user' , 'menuitem','quantity' , 'unit_price' , 'total_price'  ,'price' ]
        extra_kwargs = { 'total_price':{'write_only':True},'price': { 'read_only': True} }

    def price_of_total(self, item:m.Cart):
        item.price =item.unit_price *item.quantity *Decimal(1)
        return item.price
        
        

class Order_serializer(serializers.ModelSerializer):
    # total = serializers.DecimalField(decimal_places=2 ,max_digits=6)
    class Meta:
        model  = m.Order
        fields = ['id' , 'user_id' ,'delivery_crew' , 'status' , 'total', 'date']
        
   
        

class Order_item_serializer(serializers.ModelSerializer):
    class Meta:
        model=m.OrderItem
        fields= [ 'id' , 'order' , 'menuitem','quantity' , 'unit_price','price']
        
class Users_serlializer(serializers.ModelSerializer):
    class Meta: 
        model = m.User
        fields=['id', 'username',  'first_name' , 'last_name' , 'email' ,'groups']
