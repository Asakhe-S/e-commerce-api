from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Cart, CartItem, Product, Category, Review, Wishlist, Order, OrderItem
from .serializers import CartItemSerializer, CartSerializer, ProductListSerializer, ProductDetailSerializer, CategoryListSerializer, CategoryDetailSerializer, ReviewSerializer, WishlistSerializer   
from django.conf import settings
from django.core.cache import cache
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.
User = get_user_model()

@api_view(['GET', 'POST'])
def product_list(request):
    if request.method == 'GET':
        cached_products = cache.get('product_list')
        if cached_products:
            return Response(cached_products)
        
        products = Product.objects.all()  # Fetch all products
        serializer = ProductListSerializer(products, many=True)
        
        cache.set('product_list', serializer.data, timeout=60 * 15)  # Cache for 1 hour
        return Response(serializer.data)
    
    elif request.method == 'POST':
        data = request.data
        required_fields = ['name', 'description', 'price', 'category_id']
        
        # Validate required fields
        for field in required_fields:
            if field not in data:
                return Response({'error': f'{field} is required'}, status=400)
        
        try:
            category = Category.objects.get(id=data['category_id'])
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=404)
        
        # Create product
        product = Product.objects.create(
            name=data['name'],
            description=data['description'],
            price=data['price'],
            category=category,
            featured=data.get('featured', False)
        )
        
        # Handle image upload if provided
        if 'image' in request.FILES:
            product.image = request.FILES['image']
            product.save()
        
        serializer = ProductDetailSerializer(product)
        cache.delete('product_list')
        return Response(serializer.data, status=201)

@api_view(['PUT', 'DELETE'])
def product_detail_edit(request, pk):
    try:
        product = Product.objects.get(id=pk)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=404)
    
    if request.method == 'PUT':
        data = request.data
        
        # Update fields
        product.name = data.get('name', product.name)
        product.description = data.get('description', product.description)
        product.price = data.get('price', product.price)
        product.slug = data.get('slug', product.slug)
        product.featured = data.get('featured', product.featured)
        
        # Update category if provided
        if 'category' in data:
            try:
                category = Category.objects.get(id=data['category'])
                product.category = category
            except Category.DoesNotExist:
                return Response({'error': 'Category not found'}, status=404)
        
        # Handle image upload if provided
        if 'image' in request.FILES:
            product.image = request.FILES['image']
        
        product.save()
        serializer = ProductDetailSerializer(product)
        cache.delete('product_list')
        cache.delete(f'product_detail_{pk}')
        return Response(serializer.data)
    
    elif request.method == 'DELETE':
        product.delete()
        cache.delete('product_list')
        cache.delete(f'product_detail_{pk}')

        return Response({'message': 'Product deleted successfully'}, status=204)

@api_view(['GET'])
def product_detail(request, slug):
    cached_product = cache.get(f'product_detail_{slug}')
    if cached_product:   
         return Response(cached_product)
    product = Product.objects.get(slug=slug)  # Fetch product by slug
    serializer = ProductDetailSerializer(product)
    
    cache.set(f'product_detail_{slug}', serializer.data, timeout=60 * 15)  # Cache for 1 hour
    return Response(serializer.data)

@api_view(['GET', 'POST'])
def category_list(request):
    if request.method == 'GET':
        cached_categories = cache.get('category_list')
        if cached_categories:
            return Response(cached_categories)
        
        categories = Category.objects.all()  # Fetch all categories
        serializer = CategoryListSerializer(categories, many=True)
        
        cache.set('category_list', serializer.data, timeout=60 * 15)  # Cache for 1 hour
        return Response(serializer.data)
    
    elif request.method == 'POST':
        data = request.data
        
        # Validate required fields
        if 'name' not in data:
            return Response({'error': 'name is required'}, status=400)
        
        # Create category
        category = Category.objects.create(
            name=data['name'],
            slug=data.get('slug', '')
        )
        
        # Handle image upload if provided
        if 'image' in request.FILES:
            category.image = request.FILES['image']
            category.save()
        
        serializer = CategoryListSerializer(category)
        cache.delete('category_list')
        return Response(serializer.data, status=201)

@api_view(['GET'])
def category_detail(request, slug):
    cached_category = cache.get(f'category_detail_{slug}')
    if cached_category:   
         return Response(cached_category)
    category = Category.objects.get(slug=slug)  # Fetch category by slug
    serializer = CategoryDetailSerializer(category)
    
    cache.set(f'category_detail_{slug}', serializer.data, timeout=60 * 15)  # Cache for 1 hour
    return Response(serializer.data)

@api_view(['POST'])
def add_to_cart(request):
    cart_code = request.data.get('cart_code')
    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity', 1)
    
    if not cart_code or not product_id:
        return Response({'error': 'cart_code and product_id are required'}, status=400)
    
    try:
        cart = Cart.objects.get_or_create(cart_code=cart_code)[0]
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=404)
    
    try:
        quantity = int(quantity)
        if quantity < 1:
            return Response({'error': 'quantity must be at least 1'}, status=400)
    except (TypeError, ValueError):
        return Response({'error': 'quantity must be an integer'}, status=400)
    
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if created:
        cart_item.quantity = quantity
    else:
        cart_item.quantity += quantity
    cart_item.save()
    
    serializer = CartSerializer(cart)
    return Response(serializer.data)

@api_view(['GET'])
def get_cart(request):
    cart_code = request.query_params.get('cart_code')
    
    if not cart_code:
        return Response({'error': 'cart_code is required'}, status=400)
    
    try:
        cart = Cart.objects.get(cart_code=cart_code)
    except Cart.DoesNotExist:
        return Response({'error': 'Cart not found'}, status=404)
    
    serializer = CartSerializer(cart)
    return Response(serializer.data)

@api_view(['PUT'])
def update_cartitem_quantity(request):
    cartitem_id = request.data.get('cartitem_id') or request.data.get('item_id')
    quantity = request.data.get('quantity')

    if not cartitem_id or quantity is None:
        return Response({'error': 'cartitem_id and quantity are required'}, status=400)

    try:
        cartitem_id = int(cartitem_id)
        quantity = int(quantity)
    except (TypeError, ValueError):
        return Response({'error': 'cartitem_id and quantity must be integers'}, status=400)
    
    if quantity < 1:
        return Response({'error': 'quantity must be at least 1'}, status=400)

    try:
        cartitem = CartItem.objects.get(id=cartitem_id)
    except CartItem.DoesNotExist:
        return Response({'error': 'CartItem not found'}, status=404)

    cartitem.quantity = quantity
    cartitem.save()

    serializer = CartItemSerializer(cartitem)
    return Response({'data': serializer.data, 'message': 'Cart item quantity updated successfully'})

@api_view(['DELETE'])
def delete_cartitem(request, pk):
    try:
        cartitem = CartItem.objects.get(id=pk)
        cartitem.delete()
        return Response({'message': 'Cart item deleted successfully'}, status=204)
    except CartItem.DoesNotExist:
        return Response({'error': 'CartItem not found'}, status=404)


@api_view(['POST'])
def add_review(request):
    product_id = request.data.get('product_id')
    email = request.data.get('email')
    rating = request.data.get('rating')
    review_text = request.data.get('review', '')  # Optional review text

    if not product_id or not email or rating is None:
        return Response({'error': 'product_id, email, and rating are required'}, status=400)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=404)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

    if Review.objects.filter(product=product, user=user).exists():
        return Response({'error': 'You have already reviewed this product.'}, status=400)

    review = Review.objects.create(product=product, user=user, rating=rating, review=review_text)
    serializer = ReviewSerializer(review)
    return Response(serializer.data)

@api_view(['GET'])
def list_reviews(request):
    reviews = Review.objects.all().order_by('-created_at')
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)

@api_view(['PUT'])
def update_review(request, pk):
    try:
        review = Review.objects.get(id=pk)
    except Review.DoesNotExist:
        return Response({'error': 'Review not found'}, status=404)

    rating = request.data.get('rating')
    review_text = request.data.get('review', '')  # Optional review text

    if rating is None:
        return Response({'error': 'rating is required'}, status=400)

    review.rating = rating
    review.review = review_text
    review.save()

    serializer = ReviewSerializer(review)
    return Response(serializer.data)

@api_view(['DELETE'])
def delete_review(request, pk):
    try:
        review = Review.objects.get(id=pk)
        review.delete()
        return Response({'message': 'Review deleted successfully'}, status=204)
    except Review.DoesNotExist:
        return Response({'error': 'Review not found'}, status=404)

@api_view(['POST', 'GET'])
def add_to_wishlist(request):
    if request.method == 'GET':
        email = request.query_params.get('email')
        
        if not email:
            return Response({'error': 'email is required'}, status=400)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)
        
        wishlists = Wishlist.objects.filter(user=user)
        serializer = WishlistSerializer(wishlists, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        email = request.data.get('email')
        product_id = request.data.get('product_id')

        if not email or not product_id:
            return Response({'error': 'email and product_id are required'}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=404)

        wishlist = Wishlist.objects.filter(user=user, product=product)
        if wishlist.exists():
            wishlist.delete()
            return Response({'message': 'Product removed from wishlist'}, status=200)

        new_wishlist = Wishlist.objects.create(user=user, product=product)
        serializer = WishlistSerializer(new_wishlist)
        return Response(serializer.data)

@api_view(['POST'])
def product_search(request):
    query = request.data.get('query')
    if not query:
        return Response({'error': 'query field is required in JSON body.'}, status=400)

    products = Product.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query) | Q(category__name__icontains=query)
    )
    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)

api_view(['POST'])
def create_checkout_session(request):
    user = request.user
    
    #Check if user is authenticated 
    if not user.is_authenticated:
        return Response({'error': 'Please log in first'}, status=401)
    
    #Get cart_code from request 
    cart_code = request.data.get('cart_code')
    if not cart_code:
        return Response({'error': 'cart_code is required'}, status=400)
    
    #Get cart using cart_code
    try:
        cart = Cart.objects.get(cart_code=cart_code)
    except Cart.DoesNotExist:
        return Response({'error': 'Cart not found'}, status=404)
    
    #Check if cart has items 
    cart_items = CartItem.objects.filter(cart=cart)
    if not cart_items.exists():
        return Response({'error': 'Cart is empty'}, status=400)
    
    #Calculate total amount 
    total_amount = sum(item.product.price * item.quantity for item in cart_items)
    
    #Create Stripe checkout session
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=int(total_amount * 100),  # Stripe expects amount in cents
            currency='usd',
            metadata={'user_id': user.id}
        )
    except stripe.error.StripeError as e:
        return Response({'error': str(e)}, status=400)
    
    #Create order in database
    order = Order.objects.create(user=user, total_amount=total_amount, status='pending', stripe_payment_intent=payment_intent.id)
    
    #Create Order items 
    for item in cart_items:
        OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity, price=item.product.price)
    
    return Response({'client_secret': payment_intent.client_secret, 'order_id': order.id, 'total_amount': total_amount},status=201)

 