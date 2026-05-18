from django.contrib import admin
from .models import Coffee, ContactMessage, Order, OrderItem, Review

@admin.register(Coffee)
class CoffeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'description_short', 'image_preview')
    search_fields = ('name', 'description')
    list_filter = ('price',)
    
    def description_short(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_short.short_description = 'Description'
    
    def image_preview(self, obj):
        from django.utils.html import format_html
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.image.url)
        return "-"
    image_preview.short_description = 'Image Preview'

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject_short', 'sent_at')
    list_filter = ('sent_at',)
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('sent_at',)
    
    def subject_short(self, obj):
        return obj.subject[:30] + '...' if len(obj.subject) > 30 else obj.subject
    subject_short.short_description = 'Subject'

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('coffee', 'quantity', 'price', 'item_total')
    fields = ('coffee', 'quantity', 'price', 'item_total')
    can_delete = False
    
    def item_total(self, obj):
        return f"${obj.price * obj.quantity:.2f}"
    item_total.short_description = 'Total'

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'order_date', 'status', 'total_price_display')
    list_filter = ('status', 'order_date')
    search_fields = ('user__username', 'id')
    readonly_fields = ('order_date', 'total_price_display')
    inlines = [OrderItemInline]
    actions = ['mark_as_completed']
    
    def total_price_display(self, obj):
        return f"${obj.total_price:.2f}"
    total_price_display.short_description = 'Total Price'
    
    def mark_as_completed(self, request, queryset):
        queryset.update(status='Completed')
    mark_as_completed.short_description = "Mark selected orders as Completed"

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'rating', 'created_at')
    search_fields = ('name', 'message')