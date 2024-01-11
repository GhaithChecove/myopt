from django.db import models
from django.contrib.auth.models import User
# Create your models here.



class Category(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=255 ,db_index=True )

    def __str__(self) -> str:
        return self.title

class MenuItem(models.Model):
    title = models.CharField(max_length=255 , db_index=True )
    category = models.ForeignKey(Category, verbose_name=("Category"), on_delete=models.PROTECT)
    price = models.DecimalField( max_digits=6, decimal_places=2 , db_index=True)
    featured = models.BooleanField(db_index=True)


    def __str__(self) -> str:
        return self.title


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, verbose_name=("Menu Item"), on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField( max_digits=6, decimal_places=2)
    price = models.DecimalField( max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ('menuitem' , 'user')


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(User, related_name='delivery_crew', on_delete=models.SET_NULL , null=True)
    status  = models.BooleanField(db_index=True , default=False)
    total = models.DecimalField( max_digits=6, decimal_places=2)
    date = models.DateField(auto_now=True , db_index=True)


class OrderItem(models.Model):
    order = models.ForeignKey(User,  on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField( max_digits=6, decimal_places=2)
    price = models.DecimalField( max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ('order' , 'menuitem')

