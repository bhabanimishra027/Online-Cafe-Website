from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class Coffee(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Changed from IntegerField
    description = models.TextField()
    image = models.ImageField(upload_to='coffee_images/')

    def __str__(self):
        return f"{self.name} - ${self.price}"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        ordering = ['-order_date']

    def __str__(self):
        return f"Order #{self.id} - {self.user.username} - ${self.total_price}"

    def calculate_total(self):
        """Calculates and updates the total price"""
        self.total_price = sum(
            item.price * item.quantity 
            for item in self.items.all()
        )
        self.save()
        return self.total_price

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    coffee = models.ForeignKey(Coffee, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of purchase

    def __str__(self):
        return f"{self.quantity}x {self.coffee.name} (${self.price} each)"

    def save(self, *args, **kwargs):
        """Automatically set price from coffee if not set"""
        if not self.price:
            self.price = self.coffee.price
        super().save(*args, **kwargs)
        self.order.calculate_total()  # Update order total after save

    def item_total(self):
        return self.price * self.quantity
    
class Review(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='review_images/', blank=True, null=True)
    rating = models.IntegerField(default=0)  # from 1 to 5
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.rating} stars"