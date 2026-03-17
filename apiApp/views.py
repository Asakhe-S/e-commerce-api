from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Cart, CartItem, Product, Category, Review, Wishlist
from .serializers import CartItemSerializer, CartSerializer, ProductListSerializer, ProductDetailSerializer, CategoryListSerializer, CategoryDetailSerializer, ReviewSerializer, WishlistSerializer   
from django.conf import settings
# Create your views here.
User = get_user_model()

@api_view(['GET'])
def product_list(request):
    products = Product.objects.filter(featured=True)  # Fetch all products
    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def product_detail(request, slug):
    product = Product.objects.get(slug=slug)  # Fetch product by slug
    serializer = ProductDetailSerializer(product)   
    return Response(serializer.data)

@api_view(['GET'])
def category_list(request):
    categories = Category.objects.all()  # Fetch all categories
    serializer = CategoryListSerializer(categories, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def category_detail(request, slug):
    category = Category.objects.get(slug=slug)  # Fetch category by slug
    serializer = CategoryDetailSerializer(category)   
    return Response(serializer.data)

@api_view(['POST'])
def add_to_cart(request):
    cart_code = request.data.get('cart_code')
    product_id = request.data.get('product_id')
    
    cart, created = Cart.objects.get_or_create(cart_code=cart_code)
    product = Product.objects.get(id=product_id)
    
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    cart_item.quantity = 1
    cart_item.save()
    
    serializer = CartSerializer(cart)
    return Response(serializer.data)

@api_view(['PUT'])
def update_cartitem_quantity(request):
    cartitem_id = request.data.get('item_id')
    quantity = request.data.get('quantity')
    
    quantity = int(quantity)
    
    cartitem = CartItem.objects.get(id=cartitem_id)
    cartitem.quantity = quantity
    cartitem.save()
    
    serializer = CartItemSerializer(cartitem)
    return Response({'data': serializer.data, 'message': 'Cart item quantity updated successfully'})

@api_view(['DELETE'])
def delete_cartitem(request, pk):
    cartitem = CartItem.objects.get(id=pk)
    cartitem.delete()
    return Response('Cart item deleted successfully', status=204)


@api_view(['POST'])
def add_review(request):
    product_id = request.data.get('product_id')
    email = request.data.get('email')
    rating = request.data.get('rating')
    review_text = request.data.get('review', '')  # Optional review text
    
    product = Product.objects.get(id=product_id)
    user = User.objects.get(email=email)
    
    if Review.objects.filter(product=product, user=user).exists():
        return Response({'error': 'You have already reviewed this product.'}, status=400)
    
    review = Review.objects.create(product=product, user=user, rating=rating, review=review_text)
    serializer = ReviewSerializer(review)
    return Response(serializer.data)

@api_view(['PUT'])
def update_review(request, pk):
    review = Review.objects.get(id=pk)
    rating = request.data.get('rating')
    review_text = request.data.get('review', '')  # Optional review text
    
    review.rating = rating
    review.review = review_text
    review.save()
    
    serializer = ReviewSerializer(review)
    return Response(serializer.data)

@api_view(['DELETE'])
def delete_review(request, pk):
    review = Review.objects.get(id=pk)
    review.delete()
    return Response('Review deleted successfully', status=204)

@api_view(['POST'])
def add_to_wishlist(request):
    email = request.data.get('email')
    product_id = request.data.get('product_id')
    
    user = User.objects.get(email=email)
    product = Product.objects.get(id=product_id)
    
    wishlist = Wishlist.objects.filter(user=user, product=product)
    if wishlist.exists():
        wishlist.delete()
        return Response({'message': 'Product removed from wishlist'}, status=200)
    
    new_wishlist = Wishlist.objects.create(user=user, product=product)
    serializer = WishlistSerializer(new_wishlist)
    return Response(serializer.data)

@api_view(['GET'])
def product_search(request):
    query = request.query_params.get('query')
    if not query:
        return Response({'error': 'Query parameter is required.'}, status=400)
    
    products = Product.objects.filter (Q(name__icontains=query) | Q(description__icontains=query) | Q(category__name__icontains=query))
    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)