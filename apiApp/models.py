from django.conf import settings
from django.db import models
from django.utils.text import slugify   
from django.contrib.auth.models import AbstractUser

# Create your models here.
#customizing the user model

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)  
    profile_picture_url = models.URLField(blank=True, null=True) # we are going login from google so we will get profile pic url from there
    
    def __str__(self):
        return self.email
    
    #creating category model
    
class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='category_images', blank=True, null=True)
    
    def __str__(self):
        return self.name 
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            unique_slug = self.slug
            counter = 1
            if Product.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{self.slug}-{counter}"
                counter += 1
            self.slug = unique_slug
            
        super().save(*args, **kwargs)    
    
  #creating product model  
    
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='product_images', blank=True, null=True)
    featured = models.BooleanField(default=False)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE) 
    
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            unique_slug = self.slug
            counter = 1
            if Product.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{self.slug}-{counter}"
                counter += 1
            self.slug = unique_slug
            
        super().save(*args, **kwargs)
        
        
class Cart(models.Model):       #creates a table called cart in the database
   cart_code = models.CharField(max_length=11, unique=True)
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)
   
   def __str__(self):
       return self.cart_code

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='cartitems', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='item')
    quantity = models.PositiveIntegerField(default=1)
   
   
    def __str__(self):
        return f"{self.quantity} of {self.product.name} in cart {self.cart.cart_code}"
    
    
    
class Review(models.Model):
    RATING_CHOICES =[
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]
    
    
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    review = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"
    
    class Meta:
        unique_together = ('product', 'user')  # ensures a user can only leave one review per product
        ordering = ['-created_at']  # orders reviews by most recent first
        
        
class ProductRating(models.Model):
    product = models.OneToOneField(Product, related_name='rating', on_delete=models.CASCADE)
    average_rating = models.FloatField(default=0.0)
    total_reviews = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"Rating for {self.product.name}: {self.average_rating} based on {self.total_revuews} reviews"
 
 
class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='wishlists', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='wishlist', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'product')  # ensures a user can only wishlist a product once
        ordering = ['-created']  # orders wishlists by most recent first
    
    def __str__(self):
        return f"{self.user.username} wishlisted {self.product.name}" 