from django.db import models
from django.contrib.auth.models import AbstractUser


class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название товара')
    characteristics = models.TextField(verbose_name='Описание товара')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    image = models.URLField(null=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name


class User(AbstractUser):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.email


class Order(models.Model):
    STATUS_CHOICES = (
        ('created', 'Создан'),
        ('preparing', 'Собирается'),
        ('shipped', 'Отправляется'),
        ('waiting', 'Ожидает получения'),
        ('delivered', 'Доставлен'),
    )

    full_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    order_number = models.CharField(max_length=6, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'Заказ #{self.id} - Статус: {self.get_status_display()}'

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

    def save(self, *args, **kwargs):
        if not self.id:
            last_order = Order.objects.all().order_by('id').last()
            if last_order:
                self.order_number = '{:06}'.format(int(last_order.order_number) + 1)
            else:
                self.order_number = '000001'
        super(Order, self).save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.DO_NOTHING)
    product = models.ForeignKey('Product', on_delete=models.DO_NOTHING)  # Убедитесь, что у вас есть модель Product
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def get_cost(self):
        return self.price * self.quantity

    @property
    def total(self):
        """Общая стоимость товара в заказе."""
        return self.get_cost()

    def __str__(self):
        return f'Товар: {self.product.name}, Кол-во: {self.quantity}, Общая стоимость: {self.total:.2f}'
# Create your models here.
