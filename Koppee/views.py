from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from .models import Coffee, ContactMessage, Order, OrderItem

# Home Page
def index_view(request):
    coffees = Coffee.objects.all()
    return render(request, 'index.html', {'coffees': coffees})

# Menu / Coffee List Page
def menu_view(request):
    coffees = Coffee.objects.all()
    return render(request, 'menu.html', {'coffees': coffees})

# Coffee Detail and Review Submission
def coffee_detail_view(request, pk):
    coffee = get_object_or_404(Coffee, pk=pk)
    reviews = coffee.reviews.all()

    if request.method == 'POST' and request.user.is_authenticated:
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        if rating and comment:
            coffee.reviews.create(
                user=request.user,
                rating=rating,
                comment=comment
            )
            messages.success(request, "Review submitted successfully.")
            return redirect('coffee_detail', pk=coffee.pk)
        else:
            messages.error(request, "Please fill in all fields.")

    return render(request, 'coffee_detail.html', {'coffee': coffee, 'reviews': reviews})

# Create Order Page

@login_required
def create_order_view(request):
    coffees = Coffee.objects.all()
    if request.method == 'POST':
        try:
            with transaction.atomic():
                order = Order.objects.create(user=request.user)
                for coffee in coffees:
                    quantity = int(request.POST.get(f'quantity_{coffee.id}', 0))
                    if quantity > 0:
                        OrderItem.objects.create(
                            order=order,
                            coffee=coffee,
                            quantity=quantity,
                            price=coffee.price
                        )
                order.calculate_total()
                messages.success(request, "Order placed successfully!")
                return redirect('payment_page')  # ✅ redirect to payment page
        except Exception as e:
            messages.error(request, f"Error placing order: {e}")
            return redirect('menu')
    return render(request, 'order.html', {'coffees': coffees})

@login_required
def payment_page(request):
    if request.method == 'POST':
        # You could process payment here (dummy flow)
        return redirect('order_success.html')  # ✅ redirects to success page
    return render(request, 'payments.html')

# views.py
from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Order, OrderItem

@login_required
def payment_page(request):
    try:
        # Get the most recent order placed by the user
        latest_order = Order.objects.filter(user=request.user).first()

        if not latest_order:
            return render(request, 'payments.html', {
                'create_order_view': [],
                'total': 0
            })

        order_items = latest_order.items.all()
        total = latest_order.total_price

        return render(request, 'payments.html', {
            'create_order_view': order_items,
            'total': total
        })
    
    except Exception as e:
        return render(request, 'payments.html', {
            'create_order_view': [],
            'total': 0,
            'error': str(e)
        })


@login_required
def confirm_payment(request):
    if request.method == 'POST':
        # (You can log/save payment data if needed)
        name = request.POST.get('name')
        card = request.POST.get('card')
        expiry = request.POST.get('expiry')
        cvv = request.POST.get('cvv')
        # You can validate or mock payment success here

        return render(request, 'order_success.html')  # Make sure this template exists
    return redirect('payment_page')



# My Orders Page
@login_required
def my_orders_view(request):
    try:
        # Get orders with all related data efficiently
        orders = Order.objects.filter(user=request.user)\
                   .prefetch_related(
                       'items',
                       'items__coffee'
                   )\
                   .order_by('-order_date')
        
        # Debug output
        print(f"Found {orders.count()} orders for {request.user}")
        for order in orders:
            print(f"Order #{order.id} has {order.items.count()} items")
            for item in order.items.all():
                print(f" - {item.quantity}x {item.coffee.name} @ ${item.price}")

        return render(request, 'my_orders.html', {
            'orders': orders,
            'debug': True  # Optional for template debugging
        })
        
    except Exception as e:
        print(f"Error in my_orders_view: {str(e)}")
        messages.error(request, "Error loading your orders")
        return render(request, 'my_orders.html', {'orders': None})

# Contact Page
def contact_view(request):
    if request.method == 'POST':
        try:
            ContactMessage.objects.create(
                name=request.POST['name'],
                email=request.POST['email'],
                subject=request.POST['subject'],
                message=request.POST['message']
            )
            messages.success(request, "Message sent successfully!")
            return redirect('contact')
        except Exception as e:
            messages.error(request, f"Error sending message: {str(e)}")
    
    return render(request, 'contact.html')

# Authentication Views
def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
        
    if request.method == 'POST':
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')
        
        # Try authentication with username first
        user = authenticate(request, username=username_or_email, password=password)
        
        # If that fails, try with email
        if user is None:
            try:
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('index')
        
        messages.error(request, "Invalid username/email or password.")
    
    return render(request, 'login.html')

def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been logged out.")
    return redirect('login')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Validation
        if not all([username, email, password]):
            messages.error(request, "Please fill all fields.")
            return redirect('register')
            
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')
            
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('register')
            
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('index')
        except Exception as e:
            messages.error(request, f"Registration error: {str(e)}")
    
    return render(request, 'register.html')

from django.shortcuts import render, redirect
from .models import Review
from .forms import ReviewForm

from django.shortcuts import render, redirect
from .models import Review
from .forms import ReviewForm

def review_view(request):
    if request.method == "POST":
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('thankyou')  # ✅ Redirect to thank you page
    else:
        form = ReviewForm()

    reviews = Review.objects.all().order_by('-id')[:6]
    return render(request, "review.html", {"form": form, "review_page": reviews})

def thank_you_view(request):
    return render(request, 'thankyou.html')

