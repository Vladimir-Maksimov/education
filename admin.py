from django.contrib import admin
from .models import Product, User, Order, OrderItem

admin.site.register(Product)
admin.site.register(User)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'email',
                    'address', 'postal_code', 'city', 'paid',
                    'created', 'updated', 'status']
    list_filter = ['paid', 'created', 'updated']
    inlines = [OrderItemInline]


admin.site.register(Order, OrderAdmin)

# Register your models here.
