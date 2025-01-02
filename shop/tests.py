from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase, Client
from .models import Product, User, Order, OrderItem
from .forms import UserRegistrationForm, LoginForm, OrderCreateForm
from django.contrib.auth.hashers import check_password

User = get_user_model()

class ViewTests(TestCase):
    def setUp(self):
        """Разница между Client и User в том, что Client - неавторизованный пользователь сайта, User - авторизованный"""
        # Создаем тестового клиента
        self.client = Client(
            email='test@example.com'
        )

        # Создаем тестового пользователя
        self.user = User.objects.create_user(
            first_name='Ivan',
            last_name='Ivanov',
            username='testuser',
            email='test@example.com',
            password='password123'
        )

        # Создаем тестовый продукт
        self.product = Product.objects.create(
            name='Test Product',
            price=10,
            quantity=1
        )

    def test_index_page(self):
        """Здесь обычный пользователь Интернета заходит на главную страницу"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/index.html')

    def test_account_page_requires_login(self):
        """Так как личную страницу Client не сможет увидеть, то сперва ему нужно войти в систему, чтобы увидеть эту страницу"""
        self.client.login(username='testuser',password='password123')
        response = self.client.get(reverse('account'))
        self.assertEqual(response.status_code, 200)  # Должен перенаправлять на страницу логина
        self.assertTemplateUsed(response, 'shop/account.html')

    def test_register_page(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')

    def test_register_new_user(self):
        """Тест проверяет способность формы принимать данные о создании нового пользователя"""
        response = self.client.get(reverse('register'))
        self.client.post(reverse('register'),{
            'first_name':'Vladimir',
            'last_name':'Maksimov',
            'email':'vovan@mail.ru',
            'password':'vovan'
        })

    def test_register_registered_user(self):
        response = self.client.get(reverse('register'))
        self.client.post(reverse('register'), {
            'first_name':'Ivan',
            'last_name':'Ivanov',
            'email':'test@example.com',
            'password':'password123'
        })

    def test_login_page(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_login_registered_user(self):
        response = self.client.get(reverse('login'))
        self.client.post(reverse('login'),{
            'first_name': 'Ivan',
            'last_name': 'Ivanov',
            'email': 'test@example.com',
            'password': 'password123'
        })

    def test_login_non_registered_user(self):
        response = self.client.get(reverse('login'))
        self.client.post(reverse('login'), {
            'first_name': 'someone',
            'last_name': 'something',
            'email': 'something@mail.ru',
            'password': 'somepassword'
        })

    def test_product_list_page(self):
        response = self.client.get(reverse('product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/product_list.html')

    def test_product_detail_page(self):
        response = self.client.get(reverse('product_detail', args=[self.product.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/product_detail.html')

    def test_add_to_cart(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('add_to_cart', args=[self.product.pk]), {'quantity': 1})
        self.assertEqual(response.status_code, 302)  # Перенаправление на страницу корзины
        self.assertIn(str(self.product.pk), self.client.session['cart'])

    def test_remove_from_cart(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('remove_from_cart',args=[self.product.pk]))
        self.assertEqual(response.status_code, 302)  # Перенаправление на страницу корзины
        self.assertNotIn(str(self.product.pk), self.client.session['cart'])

    def test_cart_view(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/cart.html')

    def test_create_order(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('create_order'), {
            'full_name': 'Maksimov Vladimir',
            'email': 'test@example.com',
            'adress': 'Moscow, Sovetskaya st., 1',
            'postal_code': '140125',
            'city': 'Moscow'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/order_create.html')

    def test_order_success(self):
        self.client.login(username='testuser', password='password123')
        order = Order.objects.create(email='test@example.com')
        response = self.client.get(reverse('order_success', args=[order.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/order_success.html')

class ProductModelTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name='Тестовый товар',
            characteristics='Описание тестового товара',
            price=100.00,
            quantity=10,
            image='http://example.com/image.jpg'
        )

    def test_string_representation(self):
        self.assertEqual(str(self.product), 'Тестовый товар')

    def test_product_fields(self):
        self.assertEqual(self.product.name, 'Тестовый товар')
        self.assertEqual(self.product.characteristics, 'Описание тестового товара')
        self.assertEqual(self.product.price, 100.00)
        self.assertEqual(self.product.quantity, 10)
        self.assertEqual(self.product.image, 'http://example.com/image.jpg')

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass',
            first_name='Иван',
            last_name='Иванов'
        )

    def test_string_representation(self):
            self.assertEqual(str(self.user), 'test@example.com')

    def test_user_fields(self):
        self.assertEqual(self.user.first_name, 'Иван')
        self.assertEqual(self.user.last_name, 'Иванов')
        self.assertEqual(self.user.username,'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(check_password('testpass', self.user.password))

class OrderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        self.order = Order.objects.create(
            full_name='Иван Иванов',
            email='ivan@example.com',
            address='Москва, ул. Пушкина, д. 1',
            postal_code='123456',
            city='Москва',
            paid=False,
            status='Создан'
        )

    def test_string_representation(self):
        self.assertEqual(str(self.order), f'Заказ #{self.order.id} - Статус: {self.order.status}')

    def test_order_fields(self):
        self.assertEqual(self.order.full_name, 'Иван Иванов')
        self.assertEqual(self.order.email, 'ivan@example.com')
        self.assertEqual(self.order.address, 'Москва, ул. Пушкина, д. 1')
        self.assertEqual(self.order.postal_code, '123456')
        self.assertEqual(self.order.city, 'Москва')
        self.assertFalse(self.order.paid)
        self.assertEqual(self.order.status, 'Создан')

    def test_order_number_generation(self):
        order_2 = Order.objects.create(
            full_name='Петр Петров',
            email='petr@example.com',
            address='Санкт-Петербург, ул. Ленина, д. 2',
            postal_code='654321',
            city='Санкт-Петербург',
            paid=True,
            status='shipped'
        )
        self.assertEqual(order_2.order_number, '000002')

class OrderItemModelTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name='Тестовый товар', characteristics='Описание', price=100.00,quantity=5)
        self.order = Order.objects.create(
            full_name='Иван Иванов',
            email='ivan@example.com',
            address='Москва, ул. Пушкина, д. 1',
            postal_code='123456',
            city='Москва',
            paid=False,
        )
        self.order_item = OrderItem.objects.create(order=self.order, product=self.product, quantity=2, price=100.00)

    def test_string_representation(self):
        self.assertEqual(str(self.order_item), f'Товар: {self.product.name}, Кол-во: 2, Общая стоимость: 200.00')

    def test_get_cost(self):
        self.assertEqual(self.order_item.get_cost(), 200.00)

    def test_total_property(self):
        self.assertEqual(self.order_item.total, 200.00)

class UserRegistrationFormTests(TestCase):
    def test_user_registration_form_valid(self):
        form_data = {
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'email': 'ivan@example.com',
            'password': 'securepassword',
            'password2': 'securepassword'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['first_name'], 'Иван')

    def test_user_registration_form_password_mismatch(self):
        form_data = {
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'email': 'ivan@example.com',
            'password': 'securepassword',
            'password2': 'differentpassword'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

class LoginFormTests(TestCase):
    def test_login_form_valid(self):
        form_data = {
            'email': 'ivan@example.com',
            'password': 'securepassword'
        }
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['email'], 'ivan@example.com')

    def test_login_form_invalid_email(self):
        form_data = {
            'email': '',
            'password': 'securepassword'
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

class OrderCreateFormTests(TestCase):
    def test_order_create_form_valid(self):
        form_data = {
            'full_name': 'Иван Иванов',
            'email': 'ivan@example.com',
            'address': 'Ленина, 1',
            'postal_code': '123456',
            'city': 'Москва'
        }
        form = OrderCreateForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['full_name'], 'Иван Иванов')

    def test_order_create_form_invalid_email(self):
        form_data = {
            'full_name': 'Иван Иванов',
            'email': 'invalid-email',
            'address': 'Ленина, 1',
            'postal_code': '123456',
            'city': 'Москва'
        }
        form = OrderCreateForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

# Create your tests here.
