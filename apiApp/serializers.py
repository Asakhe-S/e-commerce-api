from rest_framework import serializers
from .models import Cart, Product, Category, CartItem, Review, Wishlist
from django.contrib.auth import get_user_model       


class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name','price', 'slug', 'image']
        
        
class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name','price','description' 'slug', 'image']       
        
class CategoryListSerializer(serializers.ModelSerializer):   
    class Meta:
        model = Category
        fields = ['id', 'name', 'image', 'slug',]
        
class CategoryDetailSerializer(serializers.ModelSerializer):
    products = ProductListSerializer(many=True, read_only=True)  # nested serializer to include products in category details    
    class Meta:
        model = Category
        fields = ['id', 'name', 'image', 'slug', 'products ']        
        
        
class CartItemSerializer(serializers.Serializer):
    Product = ProductListSerializer(read_only=True)
    sub_total = serializers.SerializerMethodField()
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity','sub_total']
        
    def get_sub_total(self, cartitem):
        total = cartitem.product.price * cartitem.quantity
        return total
    
class CartSerializer(serializers.Serializer):
    cartitems = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['id', 'cart_code', 'cartitems', 'total']
        
        
    def get_total(self, cart):
        items = cart.cartitems.all()
        total = sum([item.product.price * item.quantity for item in items])
        return total
    
    
class CartStatSerializer(serializers.ModelSerializer):
    total_quantity = serializers.SerializerMethodField()
    class Meta:
        model = CartItem
        fields = ['id', 'cart_code', 'total_quantity']
        
    def get_total_quantity(self, cart):
        items = cart.cartitems.all()
        total_quantity = sum([item.quantity for item in items])
        return total_quantity
    
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'first_name', 'last_name', 'profile_picture_url']
        
        
class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'rating', 'review', 'created_at', 'updated_at']
        
        
class WishlistSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    product = ProductListSerializer(read_only=True)
    class Meta:
        model = Wishlist
        fields = ['id', 'product', 'user5', 'created']